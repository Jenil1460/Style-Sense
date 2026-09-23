"""
ModelRegistry — Centralized, High-Performance ML Model & Precomputed Embedding Registry for StyleSense AI.

Features:
- Single instance of YOLO, YOLO-Pose, CLIP ViT-B-32, MediaPipe FaceLandmarker, MediaPipe FaceMesh
- Pre-computed normalized text embeddings for all static prompt categories (eliminates runtime text encoding)
- GPU/CPU device awareness & torch.inference_mode()
- Lifespan warm-up routines to eliminate cold starts
"""

import os
import sys
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# Auto-resolve backend directory
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_possible_sites = [
    os.path.join(_backend_dir, "venv", "Lib", "site-packages"),
    os.path.join(_backend_dir, "venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages"),
]
for p in _possible_sites:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)


# Static Prompt Definitions
STYLE_LABELS = [
    "a person wearing casual everyday clothes",
    "a person wearing minimal clean outfit",
    "a person wearing streetwear urban fashion",
    "a person wearing business casual office attire",
    "a person wearing formal suit or dress",
    "a person wearing luxury designer fashion",
    "a person wearing old money preppy style",
    "a person wearing athletic sportswear",
    "a person wearing vintage retro clothing",
    "a person wearing traditional ethnic clothing",
]

STYLE_NAMES = [
    "Casual", "Minimal", "Streetwear", "Business Casual",
    "Formal", "Luxury", "Old Money", "Athleisure", "Vintage", "Traditional",
]

OCCASION_LABELS = [
    "a person dressed for everyday daily activities",
    "a person dressed for office work",
    "a person dressed for a formal event",
    "a person dressed for outdoor activities",
    "a person dressed for college or school",
    "a person dressed for a party or night out",
    "a person dressed for travel",
]

OCCASION_NAMES = [
    "Daily Wear", "Office", "Formal Event", "Outdoor", "College", "Party / Night Out", "Travel",
]

UPPER_GARMENT_KEYS = ["t-shirt", "shirt", "top", "blouse", "sweater", "hoodie", "jacket", "coat", "blazer", "dress"]
UPPER_GARMENT_PROMPTS = [f"a photo of a person wearing a {g}" for g in UPPER_GARMENT_KEYS]

LOWER_GARMENT_KEYS = ["jeans", "trousers", "chinos", "formal pants", "joggers", "sweatpants", "shorts", "skirt"]
LOWER_GARMENT_PROMPTS = [f"a photo of a person wearing {g}" for g in LOWER_GARMENT_KEYS]

FOOTWEAR_KEYS = ["sneakers", "running shoes", "sandals", "flip flops", "shoes", "boots", "loafers", "dress shoes", "heels"]
FOOTWEAR_PROMPTS = [f"a photo of {g}" for g in FOOTWEAR_KEYS]

HEADWEAR_KEYS = ["baseball cap", "hat", "no hat"]
HEADWEAR_PROMPTS = [f"a photo of a person wearing {g}" for g in HEADWEAR_KEYS]

PERSON_VERIFY_PROMPTS = [
    "a photograph of a person, human, man, or woman",
    "a photograph of a machine, vehicle, animal, food, product, or landscape with no people",
]


class ModelRegistry:
    _instance: Optional["ModelRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.device = "cpu"
        self._yolo_person = None
        self._yolo_pose = None
        self._clip_model = None
        self._clip_preprocess = None
        self._clip_tokenizer = None
        self._face_landmarker = None
        self._face_mesh = None

        # Pre-computed normalized text embeddings dictionary
        self._text_embeddings: Dict[str, Any] = {}
        self._initialized = True

    def initialize(self):
        """Initializes all models and precomputes text embeddings."""
        import torch

        if torch.cuda.is_available():
            self.device = "cuda"
            logger.info("[ModelRegistry] GPU acceleration enabled (CUDA).")
        else:
            self.device = "cpu"
            # Optimal CPU thread usage for PyTorch inference
            torch.set_num_threads(min(8, os.cpu_count() or 4))
            logger.info(f"[ModelRegistry] Running on CPU with {torch.get_num_threads()} inference threads.")

        self.get_yolo_person()
        self.get_yolo_pose()
        self.get_clip()
        self._precompute_clip_text_embeddings()
        self.get_face_landmarker()
        self.get_face_mesh()
        logger.info("[ModelRegistry] All models & precomputed embeddings ready.")

    def warmup(self):
        """Performs lightweight dummy inference to warm up kernels/pipelines."""
        try:
            logger.info("[ModelRegistry] Warming up models...")
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)

            # Warmup YOLO
            if self._yolo_person is not None:
                self._yolo_person.predict(source=dummy_img, imgsz=640, verbose=False)

            # Warmup YOLO-Pose
            if self._yolo_pose is not None:
                self._yolo_pose.predict(source=dummy_img, imgsz=640, verbose=False)

            # Warmup CLIP
            if self._clip_model is not None and self._clip_preprocess is not None:
                from PIL import Image as PILImage
                import torch
                pil_dummy = PILImage.fromarray(dummy_img)
                inp = self._clip_preprocess(pil_dummy).unsqueeze(0).to(self.device)
                with torch.inference_mode():
                    self._clip_model.encode_image(inp)

            logger.info("[ModelRegistry] Warmup complete.")
        except Exception as e:
            logger.warning(f"[ModelRegistry] Warmup warning: {e}")

    # ── YOLO PERSON ──
    def get_yolo_person(self):
        if self._yolo_person is not None:
            return self._yolo_person
        try:
            from ultralytics import YOLO
            model_path = os.path.join(_backend_dir, "yolov8n.pt")
            if not os.path.exists(model_path):
                model_path = "yolov8n.pt"
            self._yolo_person = YOLO(model_path)
            logger.info(f"[ModelRegistry] YOLOv8 person model loaded from {model_path}")
            return self._yolo_person
        except Exception as e:
            logger.error(f"[ModelRegistry] Failed to load YOLO person model: {e}")
            return None

    # ── YOLO POSE ──
    def get_yolo_pose(self):
        if self._yolo_pose is not None:
            return self._yolo_pose
        try:
            from ultralytics import YOLO
            model_path = os.path.join(_backend_dir, "yolov8n-pose.pt")
            if not os.path.exists(model_path):
                model_path = "yolov8n-pose.pt"
            self._yolo_pose = YOLO(model_path)
            logger.info(f"[ModelRegistry] YOLOv8 pose model loaded from {model_path}")
            return self._yolo_pose
        except Exception as e:
            logger.error(f"[ModelRegistry] Failed to load YOLO pose model: {e}")
            return None

    # ── CLIP MODEL ──
    def get_clip(self) -> Tuple[Any, Any, Any]:
        if self._clip_model is not None:
            return self._clip_model, self._clip_preprocess, self._clip_tokenizer
        try:
            import open_clip
            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32", pretrained="laion2b_s34b_b79k", device=self.device
            )
            tokenizer = open_clip.get_tokenizer("ViT-B-32")
            model.eval()
            self._clip_model = model
            self._clip_preprocess = preprocess
            self._clip_tokenizer = tokenizer
            logger.info(f"[ModelRegistry] CLIP ViT-B-32 loaded on {self.device}.")
            return model, preprocess, tokenizer
        except Exception as e:
            logger.error(f"[ModelRegistry] Failed to load CLIP model: {e}")
            return None, None, None

    def _precompute_clip_text_embeddings(self):
        """Precomputes normalized text embeddings for all prompt categories."""
        model, _, tokenizer = self.get_clip()
        if model is None:
            return

        import torch

        prompt_groups = {
            "style": STYLE_LABELS,
            "occasion": OCCASION_LABELS,
            "upper": UPPER_GARMENT_PROMPTS,
            "lower": LOWER_GARMENT_PROMPTS,
            "footwear": FOOTWEAR_PROMPTS,
            "headwear": HEADWEAR_PROMPTS,
            "person_verify": PERSON_VERIFY_PROMPTS,
        }

        with torch.inference_mode():
            for group_name, prompts in prompt_groups.items():
                tokens = tokenizer(prompts).to(self.device)
                text_feats = model.encode_text(tokens)
                text_feats /= text_feats.norm(dim=-1, keepdim=True)
                self._text_embeddings[group_name] = text_feats

        logger.info(f"[ModelRegistry] Precomputed CLIP text embeddings for {list(prompt_groups.keys())}.")

    def classify_crop_with_clip(self, image_bgr: np.ndarray, group_name: str, keys: List[str]) -> Optional[Dict[str, Any]]:
        """
        Ultra-fast zero-shot classification against precomputed text embeddings.
        Takes ~3-8ms compared to ~40-100ms with repeated text tokenization & encoding.
        """
        if image_bgr is None or image_bgr.size < 100:
            return None

        model, preprocess, _ = self.get_clip()
        if model is None or group_name not in self._text_embeddings:
            return None

        try:
            import cv2
            import torch
            from PIL import Image as PILImage

            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            pil_img = PILImage.fromarray(rgb)
            img_tensor = preprocess(pil_img).unsqueeze(0).to(self.device)

            text_feats = self._text_embeddings[group_name]

            with torch.inference_mode():
                img_feat = model.encode_image(img_tensor)
                img_feat /= img_feat.norm(dim=-1, keepdim=True)
                sims = (100.0 * (img_feat @ text_feats.T)).squeeze(0)
                probs = sims.softmax(dim=-1)

            best_idx = int(probs.argmax().item())
            best_conf = float(probs[best_idx].item())
            best_key = keys[best_idx] if best_idx < len(keys) else "Unknown"

            all_probs = {keys[i]: round(float(probs[i].item()), 4) for i in range(min(len(keys), len(probs)))}

            return {
                "label": best_key,
                "confidence": round(best_conf, 4),
                "probs": all_probs,
            }
        except Exception as e:
            logger.error(f"[ModelRegistry] CLIP crop classification error ({group_name}): {e}")
            return None

    def classify_style_and_occasion_fast(self, image_bgr: np.ndarray) -> Tuple[Optional[Dict[int, float]], Optional[Dict[int, float]]]:
        """
        Encodes the image ONCE and computes both style and occasion similarities.
        """
        if image_bgr is None or image_bgr.size < 100:
            return None, None

        model, preprocess, _ = self.get_clip()
        if model is None or "style" not in self._text_embeddings or "occasion" not in self._text_embeddings:
            return None, None

        try:
            import cv2
            import torch
            from PIL import Image as PILImage

            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            pil_img = PILImage.fromarray(rgb)
            img_tensor = preprocess(pil_img).unsqueeze(0).to(self.device)

            style_text_feats = self._text_embeddings["style"]
            occasion_text_feats = self._text_embeddings["occasion"]

            with torch.inference_mode():
                img_feat = model.encode_image(img_tensor)
                img_feat /= img_feat.norm(dim=-1, keepdim=True)

                style_sims = (100.0 * (img_feat @ style_text_feats.T)).squeeze(0)
                style_probs = style_sims.softmax(dim=-1)

                occ_sims = (100.0 * (img_feat @ occasion_text_feats.T)).squeeze(0)
                occ_probs = occ_sims.softmax(dim=-1)

            style_scores = {i: round(float(style_probs[i].item()), 4) for i in range(len(STYLE_LABELS))}
            occ_scores = {i: round(float(occ_probs[i].item()), 4) for i in range(len(OCCASION_LABELS))}

            return style_scores, occ_scores
        except Exception as e:
            logger.error(f"[ModelRegistry] Style & occasion fast classification error: {e}")
            return None, None

    # ── MEDIAPIPE FACE LANDMARKER ──
    def get_face_landmarker(self):
        if self._face_landmarker is not None:
            return self._face_landmarker if self._face_landmarker is not False else None
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            import urllib.request

            model_path = os.path.join(_backend_dir, "face_landmarker.task")
            if not os.path.exists(model_path):
                logger.info("[ModelRegistry] Downloading face_landmarker.task model...")
                url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                urllib.request.urlretrieve(url, model_path)

            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=5,
                min_face_detection_confidence=0.3,
                min_face_presence_confidence=0.3,
            )
            self._face_landmarker = vision.FaceLandmarker.create_from_options(options)
            logger.info("[ModelRegistry] MediaPipe FaceLandmarker loaded successfully.")
            return self._face_landmarker
        except Exception as e:
            logger.error(f"[ModelRegistry] MediaPipe FaceLandmarker load failed: {e}")
            self._face_landmarker = False
            return None

    # ── MEDIAPIPE FACE MESH / LANDMARKER ──
    def get_face_mesh(self):
        return self.get_face_landmarker()


# Global registry singleton
model_registry = ModelRegistry()
