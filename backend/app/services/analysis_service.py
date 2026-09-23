"""
FashionAnalysisService — High-Performance Zero-Hallucination Pipeline Orchestrator for StyleSense AI.

Optimizations:
- Unified AnalysisContext (single download & single decode with max 1280px ML copy)
- ModelRegistry singletons & pre-computed CLIP text embeddings
- Parallelized multi-task inference via asyncio.gather
- Deterministic SHA-256 + ANALYSIS_VERSION caching
- Zero redundant network requests and zero redundant tensor conversions
- High-resolution [PERF] stage timing
"""

import asyncio
import logging
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional

from app.database.mongodb import get_database
from app.utils.exceptions import APIException
from app.utils.perf_timer import PerfTimer
from app.services.ml.analysis_context import AnalysisContext
from app.ai.person_detector import PersonDetector
from app.ai.clothing_detector import ClothingDetector
from app.ai.skin_tone_estimator import SkinToneEstimator
from app.ai.pose_detector import PoseDetector
from app.ai.body_segmenter import BodySegmenter
from app.ai.body_type_estimator import BodyTypeEstimator
from app.ai.face_shape_detector import FaceShapeDetector
from app.services.ml.style_engine import StyleEngine
from app.services.ml.scoring_engine import ScoringEngine
from app.services.ml.season_detector import SeasonDetector
from app.services.personal_color_service import PersonalColorService

logger = logging.getLogger(__name__)

ANALYSIS_VERSION = "v2"


def _safe_str(oid) -> str:
    return str(oid)


class FashionAnalysisService:

    @staticmethod
    def _serialize(analysis: dict) -> dict:
        analysis["id"] = _safe_str(analysis.pop("_id"))
        analysis["upload_id"] = _safe_str(analysis["upload_id"])
        if "user_id" not in analysis:
            analysis["user_id"] = ""
        return analysis

    @staticmethod
    async def analyze_upload(user_id: str, upload_id: str, selected_person_index: Optional[int] = None) -> dict:
        timer = PerfTimer()
        db = get_database()

        # ═══ STAGE 0: Fetch Upload Record ═══
        with timer.stage("stage0_fetch_upload"):
            upload = await db.uploads.find_one({
                "_id": ObjectId(upload_id),
                "user_id": user_id
            })
            if not upload:
                raise APIException(status_code=404, detail="Upload not found.")

        # Check for upload_id cached analysis (bypass cache if selected_person_index is explicitly supplied)
        existing = await db.analysis.find_one({"upload_id": ObjectId(upload_id)})
        if existing and selected_person_index is None and existing.get("garments") and existing.get("explainability") and existing.get("body_visibility") and existing.get("analysis_version") == ANALYSIS_VERSION:
            logger.info(f"Returning cached analysis for upload {upload_id}")
            return FashionAnalysisService._serialize(existing)
        elif existing and existing.get("analysis_version") != ANALYSIS_VERSION:
            logger.info(f"Invalidating stale analysis version for upload {upload_id}")
            await db.analysis.delete_one({"_id": existing["_id"]})

        image_url = upload["image_url"]
        logger.info(f"═══ PIPELINE START: upload {upload_id} ═══")
        audit_trail = []

        # ═══ STAGE 0b: Build Shared AnalysisContext (Download once, decode once, resize ML copy) ═══
        with timer.stage("image_prep"):
            try:
                context = await AnalysisContext.create(upload_id=upload_id, image_url=image_url)
            except Exception as e:
                logger.error(f"[AnalysisService] Failed to prepare image: {e}")
                raise APIException(status_code=400, detail="Could not download or decode image. Please check the file and try again.")

        # Deterministic SHA-256 Hash Cache Check
        if selected_person_index is None:
            cached_by_hash = await db.analysis.find_one({
                "image_hash": context.image_hash,
                "analysis_version": ANALYSIS_VERSION,
                "garments": {"$exists": True, "$ne": []}
            })
            if cached_by_hash and cached_by_hash.get("garments"):
                logger.info(f"Returning SHA-256 cache hit ({context.image_hash[:10]}) for upload {upload_id}")
                cached_by_hash["upload_id"] = ObjectId(upload_id)
                cached_by_hash["user_id"] = user_id
                # Update upload status
                await db.uploads.update_one(
                    {"_id": ObjectId(upload_id)},
                    {"$set": {"status": "analyzed"}}
                )
                timer.log_summary(f"[PERF Cache Hit upload={upload_id}]")
                return FashionAnalysisService._serialize(cached_by_hash)

        # ═══ STAGE 1: Person Detection (YOLO) — GATE ═══
        with timer.stage("person_detection"):
            audit_trail.append("Stage 1: Person Detection")
            person_detection = await PersonDetector.detect(context)
            context.person_detection = person_detection
            logger.info(f"[Stage 1] Person: detected={person_detection.get('detected')} conf={person_detection.get('confidence')}")

        if not person_detection.get("detected", False):
            reason = person_detection.get("reason", "")
            evidence = person_detection.get("evidence", "")
            detail_map = {
                "download_failed": "Could not download the image. Please check network or re-upload.",
                "decode_failed": "Could not decode image. Please upload a valid JPEG, PNG, or WEBP.",
                "model_unavailable": "AI Person Detection model failed to initialize. Please try again.",
                "clip_rejected_not_person": "This image does not appear to contain a person. Please upload a photo of yourself wearing an outfit.",
            }
            detail = detail_map.get(
                reason,
                "Could not detect a person in this image. Please upload a clear, well-lit photo showing a person wearing an outfit. "
                "Try a full-body or upper-body photo with good lighting."
            )
            logger.warning(f"[Stage 1] Person detection failed: reason={reason}, evidence={evidence}")
            raise APIException(status_code=400, detail=detail)

        # ═══ STAGE 2: Pose Detection (YOLO-Pose) ═══
        with timer.stage("pose_detection"):
            audit_trail.append("Stage 2: Pose Detection")
            pose = await PoseDetector.detect(context, person_detection)
            context.pose = pose
            logger.info(f"[Stage 2] Pose: {pose.get('pose_type')} conf={pose.get('overall_confidence')}")

        # ═══ STAGE 3: Body Visibility ═══
        audit_trail.append("Stage 3: Body Visibility")
        lower_body_visible = pose.get("lower_body_visible", False)
        feet_visible = pose.get("feet_visible", False)
        upper_body_visible = pose.get("upper_body_visible", False)
        body_visibility = pose.get("body_visibility", {})

        # ═══ STAGE 4: Garment Segmentation (Landmark-guided GrabCut) ═══
        with timer.stage("segmentation"):
            audit_trail.append("Stage 4: Garment Segmentation")
            segmentation = await BodySegmenter.segment(context, person_detection, pose)
            context.segmentation = segmentation
            context.crops = segmentation.get("crops", {})
            context.masks = segmentation.get("masks", {})
            context.regions = segmentation.get("regions", {})
            logger.info(f"[Stage 4] Segmentation: {segmentation.get('evidence', 'none')}")

        # ═══ STAGE 5: CONCURRENT ANALYSIS PHASE (All independent models run in parallel) ═══
        with timer.stage("parallel_models"):
            audit_trail.append("Stage 5: Parallel Multi-Model Inference")

            task_skin = SkinToneEstimator.estimate(
                context, person_detection, segmentation, selected_person_index=selected_person_index
            )
            task_face = FaceShapeDetector.detect(context)
            task_clothing = ClothingDetector.detect(context, person_detection, pose, segmentation)
            task_colors = StyleEngine.extract_colors(context, segmentation)
            task_style = StyleEngine.classify_style(None, None, context, segmentation)
            task_body = BodyTypeEstimator.estimate(None, pose, person_detection)

            (
                skin_tone_result,
                face_shape_result,
                clothing_result,
                colors,
                styles,
                body_type_result
            ) = await asyncio.gather(
                task_skin,
                task_face,
                task_clothing,
                task_colors,
                task_style,
                task_body
            )

        garments = clothing_result.get("garments", [])
        clothing_items = clothing_result.get("clothing_detected", [])
        logger.info(f"[Parallel Phase Done] Garments={len(garments)} Primary color={colors.get('primary')} Style={styles[0].get('style_name') if styles else 'None'}")

        # ═══ STAGE 6: Occasion, Season & Personal Color Recommendations ═══
        with timer.stage("derived_rules"):
            audit_trail.append("Stage 6: Style & Occasion Integration")
            occasion_result = await StyleEngine.detect_occasion(styles, clothing_items, context, segmentation)
            occasion_str = occasion_result.get("occasion", "Unknown")

            personal_color_palette = PersonalColorService.generate_personal_color_recommendations(
                skin_tone_data=skin_tone_result,
                garments=garments,
                detected_colors=colors
            )
            season_result = SeasonDetector.detect_season(clothing_items, colors)
            season = season_result.get("value", "Unknown") if isinstance(season_result, dict) else season_result

            radar_metrics = ScoringEngine.calculate_radar_metrics(
                colors=colors,
                styles=styles,
                clothing_items=clothing_items,
                person_confidence=person_detection.get("confidence", 1.0),
                occasion_result=occasion_result,
            )
            fashion_score = radar_metrics["overall_score"]

            recommendations = ScoringEngine.generate_recommendations(
                score=fashion_score,
                styles=styles,
                colors=colors,
                clothing_items=clothing_items,
                skin_tone=skin_tone_result.get("tone", "Unknown"),
                occasion=occasion_str,
                person_confidence=person_detection.get("confidence", 1.0),
                body_type=body_type_result.get("body_type", "Unknown"),
                season=season,
                pose=pose,
                lower_body_visible=lower_body_visible,
                feet_visible=feet_visible,
            )

        # ═══ STAGE 7: Debug Visualizer & Gemini AI Summary ═══
        async def _run_gemini_summary():
            try:
                from app.services.ml.gemini_client import get_gemini_client
                gemini_client = get_gemini_client()
                if not gemini_client:
                    return None

                garment_desc = ", ".join(
                    f"{g.get('color', '')} {g.get('item', g.get('garment', ''))}".strip()
                    for g in garments
                ) or "No garments detected"
                top_style_name = styles[0].get("style_name", "Unknown") if styles else "Unknown"
                top_style_conf = styles[0].get("confidence", 0) if styles else 0

                summary_prompt = (
                    f"You are an expert AI fashion stylist. Write a concise, insightful 2-3 sentence "
                    f"fashion analysis summary for a user.\n\n"
                    f"Detected outfit: {garment_desc}\n"
                    f"Primary color: {colors.get('primary', 'Unknown')}\n"
                    f"Style: {top_style_name} ({top_style_conf:.0%} confidence)\n"
                    f"Occasion: {occasion_str}\n"
                    f"Season: {season}\n"
                    f"Skin tone: {skin_tone_result.get('tone', 'Unknown')}\n"
                    f"Fashion score: {fashion_score}/100\n"
                    f"Accessories score: {radar_metrics.get('accessories', 'N/A')}%\n\n"
                    f"Write a natural, personalized analysis. Reference the actual detected items. "
                    f"Include one specific improvement suggestion. Keep it under 3 sentences."
                )

                summary_interaction = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: gemini_client.interactions.create(
                            model="gemini-3.6-flash",
                            input=summary_prompt,
                            system_instruction="You are a fashion stylist. Respond with ONLY the summary text. No JSON, no markdown, no headers.",
                        )
                    ),
                    timeout=2.0
                )
                if summary_interaction and summary_interaction.output_text:
                    return summary_interaction.output_text.strip()
            except Exception as e:
                logger.debug(f"[AnalysisService] Gemini summary skipped/timed out: {e}")
            return None

        # Execute debug visualizer
        try:
            from app.utils.debug_visualizer import DebugVisualizer
            DebugVisualizer.save_debug_visuals(
                image_bgr=context.image_bgr,
                person_box=person_detection,
                landmarks=pose.get("landmarks", {}),
                garments=garments,
                crops=segmentation.get("crops", {}),
                prefix=f"upload_{upload_id}"
            )
        except Exception as e:
            logger.warning(f"[AnalysisService] Debug visualizer warning: {e}")

        with timer.stage("gemini_summary"):
            ai_summary = await _run_gemini_summary()

        # ═══ Explainability Map ═══
        explainability = {
            "person": {
                "value": "Detected" if person_detection.get("detected") else "Not Detected",
                "status": "Detected" if person_detection.get("detected") else "Not Detected",
                "confidence": person_detection.get("confidence", 0),
                "evidence": person_detection.get("evidence", ""),
                "source": person_detection.get("source", "yolo"),
            },
            "body_visibility": {
                **body_visibility,
                "source": pose.get("source", "yolo_pose"),
            },
            "clothing": [
                {
                    "item": g.get("item", g.get("garment")),
                    "value": f"{g.get('color', '')} {g.get('item', g.get('garment'))}".strip(),
                    "color": g.get("color", "Unknown"),
                    "color_confidence": g.get("color_confidence", 0),
                    "color_evidence": g.get("color_evidence", ""),
                    "bounding_box": g.get("bounding_box", {}),
                    "status": g.get("status", "Detected"),
                    "confidence": g.get("confidence", 0),
                    "evidence": g.get("evidence", ""),
                    "source": g.get("source", "yolo_clip_garment_detector"),
                } for g in garments
            ],
            "colors": {
                "value": colors.get("primary", "Unknown"),
                "status": colors.get("status", "Unknown"),
                "confidence": colors.get("confidence", 0),
                "evidence": colors.get("evidence", ""),
                "source": "kmeans_segmentation",
            },
            "styles": [
                {
                    "value": s.get("style_name", "Unknown"),
                    "confidence": s.get("confidence", 0),
                    "evidence": s.get("evidence", ""),
                    "source": "fashion_clip",
                } for s in styles
            ],
            "body_type": {
                "value": body_type_result.get("body_type", "Insufficient visibility"),
                "status": body_type_result.get("status", "Insufficient visibility"),
                "confidence": body_type_result.get("confidence", 0),
                "evidence": body_type_result.get("evidence", ""),
                "source": body_type_result.get("source", "mediapipe_pose"),
            },
            "face_shape": {
                "value": face_shape_result.get("face_shape", "Unknown"),
                "confidence": face_shape_result.get("confidence", 0),
                "evidence": face_shape_result.get("evidence", ""),
                "source": face_shape_result.get("source", "mediapipe"),
            },
            "skin_tone": {
                "value": skin_tone_result.get("tone", "Unknown"),
                "confidence": skin_tone_result.get("confidence", 0),
                "evidence": skin_tone_result.get("evidence", ""),
                "source": skin_tone_result.get("source", "skin_tone_estimator"),
            },
            "occasion": {
                "value": occasion_str,
                "status": occasion_result.get("status", "Unknown"),
                "confidence": occasion_result.get("confidence", 0),
                "evidence": occasion_result.get("evidence", ""),
                "source": "clip_occasion_classifier",
            },
            "season": {
                "value": season,
                "confidence": season_result.get("confidence", 0) if isinstance(season_result, dict) else 0,
                "evidence": season_result.get("evidence", "") if isinstance(season_result, dict) else "",
                "source": "season_detector",
            },
            "audit_trail": audit_trail,
        }

        # ═══ Serializable segmentation ═══
        segmentation_doc = {
            "segmented": segmentation.get("segmented", False),
            "image_dimensions": segmentation.get("image_dimensions", {}),
            "regions": segmentation.get("regions", {}),
            "mask_ready": segmentation.get("mask_ready", False),
            "evidence": segmentation.get("evidence", ""),
            "source": segmentation.get("source", ""),
        }

        # ═══ STAGE 9: Save to MongoDB ═══
        with timer.stage("db_save"):
            analysis_doc = {
                "user_id": user_id,
                "upload_id": ObjectId(upload_id),
                "image_url": image_url,
                "image_hash": context.image_hash,
                "analysis_version": ANALYSIS_VERSION,
                "person_detection": person_detection,
                "pose": {k: v for k, v in pose.items() if k != "landmarks"},
                "body_visibility": body_visibility,
                "segmentation": segmentation_doc,
                "colors": colors,
                "clothing_detected": clothing_items,
                "garments": garments,
                "lower_body_status": clothing_result.get("lower_body_status"),
                "footwear_status": clothing_result.get("footwear_status"),
                "visibility_note": clothing_result.get("visibility_note"),
                "skin_tone": skin_tone_result,
                "personal_color_palette": personal_color_palette,
                "body_type": body_type_result,
                "face_shape": face_shape_result,
                "styles": styles,
                "occasion": occasion_str,
                "occasion_details": occasion_result,
                "season": season,
                "season_details": season_result if isinstance(season_result, dict) else {"value": season},
                "fashion_score": fashion_score,
                "radar_metrics": radar_metrics,
                "recommendations": recommendations,
                "ai_summary": ai_summary,
                "explainability": explainability,
                "perf_timings": timer.get_summary(),
                "status": "completed",
                "created_at": datetime.now(timezone.utc),
            }

            result = await db.analysis.insert_one(analysis_doc)
            analysis_doc["_id"] = result.inserted_id

            await db.uploads.update_one(
                {"_id": ObjectId(upload_id)},
                {"$set": {"status": "analyzed"}}
            )

        timer.log_summary(f"[PERF Pipeline Complete upload={upload_id}]")
        logger.info(f"═══ PIPELINE COMPLETE: upload {upload_id} | Score: {fashion_score} | Total: {timer.total():.2f}s ═══")
        return FashionAnalysisService._serialize(analysis_doc)

    @staticmethod
    async def get_analysis(user_id: str, analysis_id: str) -> dict:
        db = get_database()
        analysis = await db.analysis.find_one({
            "_id": ObjectId(analysis_id),
            "user_id": user_id
        })
        if not analysis:
            raise APIException(status_code=404, detail="Analysis not found.")
        return FashionAnalysisService._serialize(analysis)

    @staticmethod
    async def get_user_analyses(user_id: str) -> List[dict]:
        db = get_database()
        cursor = db.analysis.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=50)
        return [FashionAnalysisService._serialize(doc) for doc in docs]

    @staticmethod
    async def delete_analysis(user_id: str, analysis_id: str) -> bool:
        from app.services.upload_service import UploadService
        db = get_database()

        query = {"user_id": user_id}
        if ObjectId.is_valid(analysis_id):
            query["_id"] = ObjectId(analysis_id)
        else:
            query["_id"] = analysis_id

        analysis = await db.analysis.find_one(query)

        upload_id = analysis.get("upload_id") if analysis else None
        if upload_id:
            await UploadService.delete_upload(user_id, str(upload_id))

        if analysis:
            await db.analysis.delete_one({"_id": analysis["_id"]})

        logger.info(f"Successfully deleted analysis {analysis_id} for user {user_id}")
        return True
