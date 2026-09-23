import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, Target, Shirt, AlertCircle, User, Sparkles, Wand2, Download, Bookmark, Compass, CheckCircle2, HelpCircle, EyeOff, Tag, ShieldCheck, Check, X, Bot, Palette, Lightbulb } from "lucide-react";
import { api } from "../../lib/api";
import { extractErrorMessage } from "../../lib/utils";
import toast from "react-hot-toast";
import { PersonalColorPalette } from "../../components/dashboard/PersonalColorPalette";

export function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [reloadingPerson, setReloadingPerson] = useState(false);

  const handleSelectPerson = async (personIndex: number) => {
    if (!analysis?.upload_id) return;
    setReloadingPerson(true);
    try {
      const resp = await api.post(`/ai/analyze/${analysis.upload_id}?selected_person_index=${personIndex}`);
      if (resp.data) {
        setAnalysis(resp.data);
        toast.success(`Updated analysis for Person ${personIndex + 1}`);
      }
    } catch (err: any) {
      toast.error(extractErrorMessage(err, "Failed to analyze selected person."));
    } finally {
      setReloadingPerson(false);
    }
  };

  // Virtual Try-On state
  const [tryonLoading, setTryonLoading] = useState(false);
  const [tryonStep, setTryonStep] = useState<string>("Preparing your outfit...");
  const [tryonResult, setTryonResult] = useState<string | null>(null);
  const [originalResultUrl, setOriginalResultUrl] = useState<string | null>(null);
  const [tryonEngine, setTryonEngine] = useState<string | null>(null);
  const [selectedOutfit, setSelectedOutfit] = useState<string>("");
  const [sliderPosition, setSliderPosition] = useState(50);


  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      try {
        const [analysisResp, recResp] = await Promise.allSettled([
          api.get(`/ai/analysis/${id}`),
          api.post(`/recommendations/generate/${id}`)
        ]);

        if (analysisResp.status === "fulfilled") {
          setAnalysis(analysisResp.value.data);
          if (analysisResp.value.data?.recommendations?.[0]) {
            setSelectedOutfit(analysisResp.value.data.recommendations[0]);
          }
        } else {
          throw analysisResp.reason;
        }

        if (recResp.status === "fulfilled" && recResp.value.data) {
          setRecommendation(recResp.value.data);
        }
      } catch (err: any) {
        console.error("Failed to load analysis", err);
        setError(extractErrorMessage(err, "Could not load the analysis."));
        toast.error("Failed to load analysis");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleGenerateTryOn = async () => {
    if (!id || !selectedOutfit || tryonLoading) return;
    setTryonLoading(true);
    setTryonResult(null);

    const steps = [
      "Preparing your outfit...",
      "Applying the new clothing...",
      "Finalizing your virtual try-on..."
    ];

    setTryonStep(steps[0]);
    let stepIdx = 0;
    const interval = setInterval(() => {
      stepIdx = (stepIdx + 1) % steps.length;
      setTryonStep(steps[stepIdx]);
    }, 3000);

    try {
      const formData = new FormData();
      formData.append("outfit_prompt", selectedOutfit);
      formData.append("analysis_id", id);
      if (analysis?.image_url) {
        formData.append("person_image_url", analysis.image_url);
      }

      const resp = await api.post('/virtual-try-on/generate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      clearInterval(interval);

      const isSuccess = resp.data?.success;
      const genUrl = resp.data?.generated_image_url;

      if (isSuccess && genUrl) {
        setTryonResult(genUrl);
        setOriginalResultUrl(resp.data?.original_image_url || analysis?.image_url || null);
        setTryonEngine(`Hugging Face IDM-VTON (${resp.data?.model || 'yisol/IDM-VTON'})`);
        toast.success("Virtual Try-On preview generated!");
      } else {

        setTryonResult(null);
        const errMsg = resp.data?.error || "Virtual try-on generation failed. Please try again.";
        console.error("[Virtual Try-On Error]:", errMsg);
        toast.error(errMsg, { duration: 6000 });
      }

    } catch (err: any) {
      clearInterval(interval);
      setTryonResult(null);
      const backendErr = err.response?.data?.error || err.response?.data?.message || err.message || "Virtual try-on generation failed. Please try again.";
      console.error("[OpenAI Virtual Try-On Error]:", backendErr);
      toast.error(backendErr, { duration: 6000 });
    } finally {
      setTryonLoading(false);
    }

  };

  const handleSaveToWardrobe = async () => {
    try {
      await api.post('/wardrobe', {
        category: analysis?.clothing_detected?.[0]?.region || 'Upper',
        clothing_type: analysis?.clothing_detected?.[0]?.item || 'Outfit',
        color_name: analysis?.colors?.primary || 'Neutral',
        image_url: tryonResult || analysis?.image_url,
        tags: [analysis?.occasion, analysis?.season].filter(Boolean),
      });
      toast.success("Saved to Wardrobe!");
    } catch (err) {
      toast.error("Failed to save to wardrobe.");
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col h-full min-h-[400px] items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-purple-400" />
        <p className="text-white/50 animate-pulse">Running Pre-Segmentation & Garment AI Analysis...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex flex-col h-full min-h-[400px] items-center justify-center space-y-6 max-w-md mx-auto text-center">
        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-red-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Analysis Error</h2>
          <p className="text-white/50">{error || "The requested analysis could not be processed."}</p>
        </div>
        <button
          onClick={() => navigate('/dashboard')}
          className="px-6 py-2 bg-white/5 hover:bg-white/10 rounded-full text-white transition-colors"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const colors = analysis?.colors || {};
  const styles = analysis?.styles || [];
  const garments = analysis?.garments || analysis?.clothing_detected || [];
  const skinTone = analysis?.skin_tone?.tone;
  const bodyTypeObj = analysis?.body_type || {};
  const bodyType = bodyTypeObj.body_type || "Body type cannot be estimated from this image.";
  const occasion = analysis?.occasion;
  const radar = analysis?.radar_metrics || {};
  const radarExplanations = radar.explanations || {};
  const bodyVis = analysis?.body_visibility || analysis?.pose?.body_visibility || {};
  const lowerBodyStatus = analysis?.lower_body_status || "Not Visible";
  const footwearStatus = analysis?.footwear_status || "Not Visible";
  const visibilityNote = analysis?.visibility_note || (lowerBodyStatus.includes("Not Visible") ? "Lower-body analysis is unavailable because it is outside the image." : null);

  const aiTips = recommendation?.ai_styling_tips || [];
  const aiOutfitSuggestions = recommendation?.ai_outfit_suggestions || [];
  const aiColorAdvice = recommendation?.ai_color_advice;

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-full text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">AI Fashion Analysis</h1>
            <p className="text-white/50">Segmented garment analysis, evidence scoring & explainability.</p>
          </div>
        </div>
      </div>

      {/* NEW: Gemini AI Summary Card */}
      {analysis.ai_summary && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-900/40 via-pink-900/30 to-purple-950/40 border border-purple-500/30 p-5 rounded-3xl backdrop-blur-xl relative overflow-hidden"
        >
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-500/20 rounded-2xl text-purple-300 shrink-0 border border-purple-500/30">
              <Bot className="w-6 h-6 animate-pulse text-pink-400" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-purple-200 uppercase tracking-wider">Gemini 3.6 Flash — AI Stylist Overview</h3>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/30 text-purple-200 font-mono border border-purple-400/30">AI Generated</span>
              </div>
              <p className="text-white/90 text-sm leading-relaxed font-sans">{analysis.ai_summary}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Requirement: Explicit boundary banner when lower body is outside image */}
      {visibilityNote && (
        <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-2xl flex items-center gap-3 text-amber-300">
          <EyeOff className="w-5 h-5 shrink-0" />
          <p className="text-sm font-medium">{visibilityNote}</p>
        </div>
      )}

      {/* NEW: Personal Color Palette & Skin Tone Analysis Section */}
      <PersonalColorPalette
        skinToneData={analysis.skin_tone}
        paletteData={analysis.personal_color_palette}
        uploadId={analysis.upload_id}
        onSelectPerson={handleSelectPerson}
        reloadingPerson={reloadingPerson}
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* Left Column - Image Preview & Body Visibility Panel */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-card p-2 rounded-[2rem] border-white/5 relative overflow-hidden group">
            <div className="aspect-[3/4] rounded-[1.5rem] overflow-hidden relative bg-black/50">
              <img
                src={analysis.image_url}
                alt="Outfit"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-medium text-white">Score: {analysis.fashion_score}/100</span>
              </div>
              {occasion && (
                <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span className="text-xs font-medium text-white">{occasion}</span>
                </div>
              )}
            </div>
          </div>

          {/* Body Visibility Detector Panel */}
          <div className="glass-card p-4 rounded-3xl border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-bold text-white">Body Visibility Detector</h3>
              </div>
              <span className="text-xs font-mono text-purple-300">{bodyVis.visibility_percentage || 50}% Visible</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className={`p-2 rounded-xl border flex items-center justify-between ${bodyVis.upper_body_visible !== false ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-white/40'}`}>
                <span>Upper Body</span>
                {bodyVis.upper_body_visible !== false ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              </div>

              <div className={`p-2 rounded-xl border flex items-center justify-between ${bodyVis.lower_body_visible ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-white/40'}`}>
                <span>Lower Body</span>
                {bodyVis.lower_body_visible ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              </div>

              <div className={`p-2 rounded-xl border flex items-center justify-between ${bodyVis.feet_visible ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-white/40'}`}>
                <span>Feet</span>
                {bodyVis.feet_visible ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              </div>

              <div className={`p-2 rounded-xl border flex items-center justify-between ${bodyVis.hands_visible !== false ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-white/40'}`}>
                <span>Hands</span>
                {bodyVis.hands_visible !== false ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              </div>

              <div className={`p-2 rounded-xl border flex items-center justify-between col-span-2 ${bodyVis.face_visible !== false ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-white/40'}`}>
                <span>Face</span>
                {bodyVis.face_visible !== false ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              </div>
            </div>
          </div>

          {/* Quick Phenotype Stats */}
          <div className="grid grid-cols-2 gap-3">
            {skinTone && (
              <div className="glass-card p-3 rounded-2xl border-white/5">
                <div className="flex items-center justify-between text-white/40 text-xs mb-1">
                  <div className="flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-purple-400" />
                    <span>Skin Tone</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/20">Detected</span>
                </div>
                <p className="text-white font-medium text-sm">{skinTone}</p>
              </div>
            )}

            <div className="glass-card p-3 rounded-2xl border-white/5">
              <div className="flex items-center justify-between text-white/40 text-xs mb-1">
                <div className="flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-blue-400" />
                  <span>Body Type</span>
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 rounded border ${bodyTypeObj.status === 'Estimated'
                    ? 'bg-blue-500/20 text-blue-300 border-blue-500/20'
                    : 'bg-zinc-500/20 text-zinc-400 border-zinc-500/20'
                  }`}>
                  {bodyTypeObj.status || (bodyType.includes("cannot be estimated") ? "Unknown" : "Estimated")}
                </span>
              </div>
              <p className="text-white font-medium text-xs leading-snug">{bodyType}</p>
            </div>
          </div>

        </div>

        {/* Right Column - Data & Radar Chart */}
        <div className="lg:col-span-7 space-y-6">

          {/* Radar Metrics Score Breakdown */}
          <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                  <Target className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Explainable Fashion Scoring</h3>
                  <p className="text-white/40 text-xs">Score category breakdown with gain/loss reasons.</p>
                </div>
              </div>
              <span className="text-2xl font-mono font-bold text-purple-400">{analysis.fashion_score}<span className="text-xs text-white/40">/100</span></span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-white/5 p-3 rounded-2xl border border-white/5 space-y-1">
                <div className="flex justify-between items-center">
                  <p className="text-white/60 text-xs">Color Harmony</p>
                  <span className="text-purple-400 font-mono font-bold text-sm">{radar.color_harmony || 85}%</span>
                </div>
                {radarExplanations.color_harmony && (
                  <p className="text-[11px] text-white/40 italic leading-snug">{radarExplanations.color_harmony}</p>
                )}
              </div>

              <div className="bg-white/5 p-3 rounded-2xl border border-white/5 space-y-1">
                <div className="flex justify-between items-center">
                  <p className="text-white/60 text-xs">Fit & Silhouette</p>
                  <span className="text-purple-400 font-mono font-bold text-sm">{radar.fit || 80}%</span>
                </div>
                {radarExplanations.fit && (
                  <p className="text-[11px] text-white/40 italic leading-snug">{radarExplanations.fit}</p>
                )}
              </div>

              <div className="bg-white/5 p-3 rounded-2xl border border-white/5 space-y-1">
                <div className="flex justify-between items-center">
                  <p className="text-white/60 text-xs">Style Consistency</p>
                  <span className="text-purple-400 font-mono font-bold text-sm">{radar.style_consistency || 88}%</span>
                </div>
                {radarExplanations.style_consistency && (
                  <p className="text-[11px] text-white/40 italic leading-snug">{radarExplanations.style_consistency}</p>
                )}
              </div>

              <div className="bg-white/5 p-3 rounded-2xl border border-white/5 space-y-1">
                <div className="flex justify-between items-center">
                  <p className="text-white/60 text-xs">Accessories</p>
                  <span className="text-purple-400 font-mono font-bold text-sm">{radar.accessories || 82}%</span>
                </div>
                {radarExplanations.accessories && (
                  <p className="text-[11px] text-white/40 italic leading-snug">{radarExplanations.accessories}</p>
                )}
              </div>
            </div>
          </div>

          {/* Garment Detection Panel */}
          <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-500/20 rounded-lg text-amber-400">
                  <Tag className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Garment Detection Panel</h3>
                  <p className="text-white/40 text-xs">Per-garment independent color, pattern & material analysis.</p>
                </div>
              </div>
              <span className="text-xs text-white/40 font-mono">&ge;70% Conf</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-white/40">
                    <th className="pb-2 font-medium">Garment</th>
                    <th className="pb-2 font-medium">Color</th>
                    <th className="pb-2 font-medium">Pattern</th>
                    <th className="pb-2 font-medium">Material</th>
                    <th className="pb-2 font-medium text-right">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {garments.map((g: any, idx: number) => (
                    <tr key={idx} className="text-white/80">
                      <td className="py-2.5 font-medium flex items-center gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{g.garment || g.item}</span>
                      </td>
                      <td className="py-2.5">
                        <span className="px-2 py-0.5 rounded-full bg-white/10 text-white text-[11px] border border-white/10">
                          {g.color || colors.primary || "Neutral"}
                        </span>
                      </td>
                      <td className="py-2.5 text-white/60">{g.pattern || "Solid"}</td>
                      <td className="py-2.5 text-white/60">{g.material || "Cotton"}</td>
                      <td className="py-2.5 text-right font-mono text-purple-300 font-semibold">
                        {((g.confidence || 0.8) * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))}

                  {lowerBodyStatus.includes("Not Visible") && (
                    <tr className="text-white/40 italic">
                      <td className="py-2.5 flex items-center gap-2">
                        <HelpCircle className="w-3.5 h-3.5 text-amber-400/80 shrink-0" />
                        <span>Pants / Lower Body</span>
                      </td>
                      <td className="py-2.5" colSpan={3}>Not Visible (Outside Image Boundary)</td>
                      <td className="py-2.5 text-right font-mono">--</td>
                    </tr>
                  )}

                  {footwearStatus.includes("Not Visible") && (
                    <tr className="text-white/40 italic">
                      <td className="py-2.5 flex items-center gap-2">
                        <HelpCircle className="w-3.5 h-3.5 text-amber-400/80 shrink-0" />
                        <span>Shoes / Footwear</span>
                      </td>
                      <td className="py-2.5" colSpan={3}>Not Visible (Outside Image Boundary)</td>
                      <td className="py-2.5 text-right font-mono">--</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top-3 Styles Classification */}
          <div className="glass-card p-6 rounded-3xl border-white/5">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                <Shirt className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Top-3 Style Taxonomy</h3>
            </div>
            <div className="space-y-3">
              {styles.slice(0, 3).map((style: any, idx: number) => (
                <div key={idx} className="space-y-1 bg-white/5 p-3 rounded-xl border border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-white font-medium text-sm">#{idx + 1} {style?.style_name}</span>
                    <span className="text-xs font-mono text-blue-400 font-semibold">{((style?.confidence || 0.8) * 100).toFixed(0)}%</span>
                  </div>
                  {style?.evidence && (
                    <p className="text-xs text-white/40 italic leading-snug">{style.evidence}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* NEW: Gemini 3.6 Flash AI Stylist Advice Card */}
          {(aiTips.length > 0 || aiColorAdvice || aiOutfitSuggestions.length > 0) && (
            <div className="glass-card p-6 rounded-3xl border-purple-500/20 bg-gradient-to-br from-purple-950/20 to-black/40 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white">
                    <Lightbulb className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Gemini 3.6 Flash — AI Stylist Advice</h3>
                    <p className="text-white/40 text-xs">Deep personalized styling recommendations.</p>
                  </div>
                </div>
                <span className="text-[10px] px-2.5 py-1 rounded-full bg-purple-500/20 text-purple-300 font-mono border border-purple-500/30">
                  Gemini Enhanced
                </span>
              </div>

              {/* AI Styling Tips */}
              {aiTips.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-pink-400" /> Key Styling Advice
                  </h4>
                  <ul className="space-y-2">
                    {aiTips.map((tip: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-white/80 bg-white/5 p-3 rounded-xl border border-white/5">
                        <span className="text-purple-400 font-bold">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Color Theory Advice */}
              {aiColorAdvice && (
                <div className="bg-purple-900/30 p-3 rounded-xl border border-purple-500/20 text-xs space-y-1">
                  <span className="font-bold text-purple-200 flex items-center gap-1.5">
                    <Palette className="w-3.5 h-3.5 text-purple-400" /> Color Harmony Insights:
                  </span>
                  <p className="text-white/80 leading-relaxed">{aiColorAdvice}</p>
                </div>
              )}

              {/* AI Outfit Suggestions */}
              {aiOutfitSuggestions.length > 0 && (
                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider">Suggested Outfit Combos</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {aiOutfitSuggestions.map((item: any, idx: number) => (
                      <div
                        key={idx}
                        className="bg-white/5 hover:bg-white/10 p-3 rounded-xl border border-white/5 cursor-pointer transition-colors space-y-1"
                        onClick={() => setSelectedOutfit(item.suggestion)}
                      >
                        <p className="text-xs font-semibold text-white">{item.suggestion}</p>
                        {item.pieces && (
                          <div className="flex flex-wrap gap-1 pt-1">
                            {item.pieces.map((p: string, pIdx: number) => (
                              <span key={pIdx} className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/20">
                                {p}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Evidence-Based Stylist Recommendations & VTON Outfit Suggestions */}
          <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Evidence-Based Stylist Recommendations & VTON Prompts</h3>
                  <p className="text-white/40 text-xs">Tailored outfit suggestions for your skin tone & style. Click any look to try on.</p>
                </div>
              </div>
              <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono border border-purple-500/30">
                1-Click Try-On
              </span>
            </div>

            <div className="space-y-3">
              {analysis?.recommendations?.map((rec: string, idx: number) => {
                const isNotice = rec.includes("outside") || rec.includes("omitted") || rec.includes("unavailable");
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.06 }}
                    className={`p-4 rounded-2xl border transition-all ${isNotice
                        ? 'bg-amber-500/10 border-amber-500/20 text-amber-300'
                        : 'bg-white/5 hover:bg-white/10 border-white/10 text-white space-y-2'
                      }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="min-w-6 min-h-6 rounded-full bg-purple-500/20 text-purple-300 flex items-center justify-center text-xs font-mono font-bold mt-0.5 shrink-0 border border-purple-500/30">
                          {idx + 1}
                        </div>
                        <div>
                          <p className="text-sm font-semibold leading-relaxed">{rec}</p>
                        </div>
                      </div>

                      {!isNotice && (
                        <button
                          onClick={() => {
                            setSelectedOutfit(rec);
                            toast.success(`Selected look #${idx + 1} for Virtual Try-On!`);
                            const vtonEl = document.getElementById("vton-section");
                            if (vtonEl) vtonEl.scrollIntoView({ behavior: "smooth" });
                          }}
                          className="px-3.5 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-purple-600/20 flex items-center gap-1.5 shrink-0 border border-purple-400/30"
                        >
                          <Wand2 className="w-3.5 h-3.5" />
                          <span>Try This Look</span>
                        </button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Hugging Face Virtual Try-On Section */}
          <div id="vton-section" className="glass-card p-6 rounded-3xl border-white/10 bg-gradient-to-br from-purple-950/30 to-black/50 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white">
                  <Wand2 className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-white">Hugging Face Virtual Try-On</h3>
                    <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-mono">
                      Hugging Face IDM-VTON
                    </span>
                  </div>
                  <p className="text-white/50 text-xs">
                    Photorealistic virtual try-on powered by Hugging Face yisol/IDM-VTON space.
                  </p>
                </div>
              </div>
            </div>

            {/* Target Outfit Prompt Input */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs text-white/60 font-medium font-sans">Target Outfit Prompt</label>
                <span className="text-[10px] text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-md border border-purple-500/20">
                  Hugging Face IDM-VTON
                </span>
              </div>

              <textarea
                value={selectedOutfit}
                onChange={(e) => setSelectedOutfit(e.target.value)}
                rows={2}
                disabled={tryonLoading}
                className="w-full bg-white/5 border border-white/10 rounded-2xl p-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple-500 font-sans disabled:opacity-50"
                placeholder="e.g. wear black suit, wear a white hoodie, wear a blue denim jacket, wear a beige formal blazer..."
              />

              {/* Quick Preset Buttons */}
              <div className="flex flex-wrap gap-2 pt-1">
                {["wear black suit", "wear a white hoodie", "wear a blue denim jacket", "wear a beige formal blazer"].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    disabled={tryonLoading}
                    onClick={() => setSelectedOutfit(preset)}
                    className="text-[11px] px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-purple-200 transition-all disabled:opacity-50"
                  >
                    + {preset}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleGenerateTryOn}
                disabled={tryonLoading || !selectedOutfit}
                className="flex-1 py-3 px-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-semibold rounded-full flex items-center justify-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-purple-600/30"
              >
                {tryonLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin text-purple-200" />
                    <span className="animate-pulse">{tryonStep}</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5" />
                    <span>Generate Virtual Try-On</span>
                  </>
                )}
              </button>
              {tryonResult && (
                <button
                  onClick={handleSaveToWardrobe}
                  className="px-5 py-3 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center gap-2 border border-white/10 transition-colors"
                >
                  <Bookmark className="w-4 h-4" />
                  <span>Save</span>
                </button>
              )}
            </div>

            {/* Before / After Preview */}
            {tryonResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6 pt-6 border-t border-white/10"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-white">Before / After Preview Comparison</h4>
                    <p className="text-xs text-purple-300 font-mono">
                      Requested Outfit: <span className="text-white font-bold">{selectedOutfit}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {tryonEngine && (
                      <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono border border-purple-500/30">
                        {tryonEngine}
                      </span>
                    )}
                  </div>
                </div>

                {/* Side-By-Side Comparison Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-white/70 px-1">
                      <span className="font-semibold">BEFORE (Original)</span>
                      <span className="text-[10px] text-white/40">Source Photograph</span>
                    </div>
                    <div className="aspect-[3/4] rounded-2xl overflow-hidden bg-black/60 border border-white/10">
                      <img
                        src={originalResultUrl || analysis?.image_url}
                        alt="Original Person Photograph"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-purple-300 px-1">
                      <span className="font-semibold">AFTER (Hugging Face IDM-VTON)</span>
                      <span className="text-[10px] text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded-full">IDM-VTON Generated</span>
                    </div>
                    <div className="aspect-[3/4] rounded-2xl overflow-hidden bg-black/60 border border-purple-500/30 shadow-lg shadow-purple-500/10">
                      <img
                        src={tryonResult}
                        alt="Hugging Face Virtual Try-On Result"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                </div>

                {/* Interactive Split Slider */}
                <div className="space-y-2">
                  <p className="text-xs text-center text-white/50">Drag slider to compare Before vs After:</p>
                  <div className="relative aspect-[3/4] rounded-2xl overflow-hidden bg-black/60 border border-white/10 max-w-md mx-auto">
                    <img
                      src={tryonResult}
                      alt="Hugging Face Virtual Try On"
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                    <div
                      className="absolute inset-0 overflow-hidden"
                      style={{ width: `${sliderPosition}%` }}
                    >
                      <img
                        src={originalResultUrl || analysis?.image_url}
                        alt="Original Person Photograph"
                        className="w-full h-full object-cover max-w-none"
                        style={{ width: '100%', height: '100%' }}
                      />
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={sliderPosition}
                      onChange={(e) => setSliderPosition(Number(e.target.value))}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
                    />
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_10px_rgba(255,255,255,0.8)] pointer-events-none z-10"
                      style={{ left: `${sliderPosition}%` }}
                    />
                    <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded-full text-xs text-white z-10">
                      Original
                    </div>
                    <div className="absolute bottom-3 right-3 bg-purple-600/80 backdrop-blur-md px-2.5 py-1 rounded-full text-xs text-white z-10">
                      HF Try-On
                    </div>
                  </div>
                </div>

                <div className="flex justify-center">
                  <a
                    href={tryonResult}
                    target="_blank"
                    rel="noreferrer"
                    download="stylesense-hf-virtual-tryon.jpg"
                    className="px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center gap-2 text-sm transition-colors border border-white/10"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download HF Try-On Image</span>
                  </a>
                </div>

              </motion.div>
            )}

          </div>


        </div>
      </div>
    </div>
  );
}
