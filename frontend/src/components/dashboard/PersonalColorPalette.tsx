import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Palette,
  Sparkles,
  Users,
  AlertTriangle,
  ShieldCheck,
  Info,
  Shirt,
  Copy,
  Flame,
  Layers,
  Sliders,
  Sun,
  Eye,
  CheckCircle2,
  X,
  Maximize2,
  SunMedium,
  Moon,
  Compass,
  Check,
  Award,
} from "lucide-react";
import toast from "react-hot-toast";

interface ColorPairing {
  name: string;
  hex: string;
}

interface ColorCardProps {
  name: string;
  hex: string;
  rgb: number[];
  why_it_works?: string;
  experiment_note?: string;
  best_pairings?: ColorPairing[];
  occasion_tip?: string;
}

interface OutfitComboProps {
  title: string;
  top: string;
  top_hex?: string;
  bottom: string;
  bottom_hex?: string;
  shoes: string;
  shoes_hex?: string;
  description: string;
  harmony_score?: number;
  tag?: string;
}

interface PersonalColorPaletteProps {
  skinToneData: any;
  paletteData: any;
  uploadId?: string;
  onSelectPerson?: (index: number) => void;
  reloadingPerson?: boolean;
}

export const PersonalColorPalette: React.FC<PersonalColorPaletteProps> = ({
  skinToneData,
  paletteData,
  onSelectPerson,
  reloadingPerson = false,
}) => {
  const [activeTab, setActiveTab] = useState<"palette" | "experiments" | "outfits">("palette");
  const [selectedColorForModal, setSelectedColorForModal] = useState<ColorCardProps | null>(null);
  const [modalBgMode, setModalBgMode] = useState<"dark" | "light">("dark");

  if (!skinToneData && !paletteData) return null;

  const status = skinToneData?.status || "success";
  const isUnavailable = status === "unavailable" || skinToneData?.skin_tone === "Unavailable";
  const skinTone = skinToneData?.skin_tone || paletteData?.skin_tone || "Medium";
  const undertone = skinToneData?.undertone || paletteData?.undertone || "Neutral";
  const confidence = Math.round((skinToneData?.confidence || paletteData?.confidence || 0.85) * 100);
  const evidence = skinToneData?.evidence || paletteData?.evidence || "Facial skin pixels from cheeks and forehead.";
  const itaAngle = skinToneData?.ita_angle ?? 25.0;
  const avgRgb = skinToneData?.avg_rgb || [180, 150, 120];
  const lightingNote = skinToneData?.lighting_note;
  const confidenceNote = skinToneData?.confidence_note;

  const multiPerson = skinToneData?.multiple_people_detected || (skinToneData?.people_count && skinToneData.people_count > 1);
  const peopleCount = skinToneData?.people_count || 1;
  const selectedPersonIndex = skinToneData?.selected_person_index || 0;

  // REQUIREMENT: Top 5 recommended colors
  const recommendedColors: ColorCardProps[] = (paletteData?.recommended_colors || []).slice(0, 5);
  const experimentalColors: ColorCardProps[] = paletteData?.experimental_colors || [];
  const outfitCombos: OutfitComboProps[] = paletteData?.outfit_combinations || [];
  const existingHarmony: string = paletteData?.existing_outfit_harmony || "";

  // Dynamic glow theme based on undertone
  const getGlowGradient = (u: string) => {
    if (u.includes("Warm")) {
      return "from-amber-500/15 via-orange-950/20 to-purple-950/20 border-amber-500/30";
    } else if (u.includes("Cool")) {
      return "from-cyan-500/15 via-blue-950/20 to-purple-950/20 border-cyan-500/30";
    } else {
      return "from-purple-500/15 via-pink-950/20 to-slate-950/20 border-purple-500/30";
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`Copied ${label} (${text}) to clipboard!`);
  };

  // Convert RGB to HSL for color spec sheet
  const getHslString = (rgb: number[] | undefined) => {
    if (!rgb || rgb.length < 3) return "N/A";
    const r = rgb[0] / 255, g = rgb[1] / 255, b = rgb[2] / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0, l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }
    return `${Math.round(h * 360)}°, ${Math.round(s * 100)}%, ${Math.round(l * 100)}%`;
  };

  const rankLabels = ["#1 Top Pick", "#2 Complementary", "#3 Foundation Neutral", "#4 Grounding Tone", "#5 Accent Hue"];

  return (
    <div className={`glass-card p-6 md:p-8 rounded-[2.5rem] border bg-gradient-to-br ${getGlowGradient(undertone)} backdrop-blur-2xl space-y-8 relative overflow-hidden transition-all duration-500 shadow-2xl`}>

      {/* Background Ambient Glow */}
      <div className="absolute -top-32 -right-32 w-96 h-96 bg-purple-600/15 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-pink-600/15 rounded-full blur-[100px] pointer-events-none" />

      {/* Header & Section Title */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 border-b border-white/10 pb-6 relative z-10">
        <div className="flex items-start md:items-center gap-4">
          <div className="p-3.5 bg-gradient-to-tr from-purple-600 via-pink-500 to-amber-400 rounded-2xl text-white shadow-xl shadow-purple-500/30 shrink-0">
            <Palette className="w-7 h-7 animate-pulse" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight font-sans">
                Personal Color Palette
              </h2>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-gradient-to-r from-purple-500/30 to-pink-500/30 text-purple-200 border border-purple-400/30 shadow-inner">
                Top 5 AI Color Match
              </span>
            </div>
            <p className="text-xs md:text-sm text-white/60 mt-1">
              Facial ITA° skin tone classification, undertone analysis & top 5 harmonized color recommendations.
            </p>
          </div>
        </div>

        {/* Confidence Badge */}
        {!isUnavailable && (
          <div className="flex items-center gap-3 self-start lg:self-auto">
            <div className="bg-white/5 border border-white/10 px-4 py-2.5 rounded-2xl flex items-center gap-3 backdrop-blur-md">
              <div className="p-2 bg-emerald-500/20 rounded-xl text-emerald-400 border border-emerald-500/30">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[10px] text-white/40 uppercase tracking-wider font-bold">Analysis Confidence</p>
                <p className="text-base font-mono font-bold text-emerald-400">{confidence}%</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Face Not Clear Warning */}
      {isUnavailable ? (
        <div className="bg-amber-500/10 border border-amber-500/30 p-6 rounded-3xl flex items-start gap-4 text-amber-300 backdrop-blur-md">
          <AlertTriangle className="w-7 h-7 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1.5">
            <h4 className="text-base font-bold text-white">Skin Tone Analysis Unavailable</h4>
            <p className="text-xs md:text-sm text-amber-200/80 leading-relaxed">
              {evidence || "Skin tone analysis is unavailable because the face is not clearly visible in the photo."}
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* Multi-Person Selector */}
          {multiPerson && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-purple-900/40 via-pink-900/30 to-purple-950/40 border border-purple-500/30 p-4 md:p-5 rounded-3xl space-y-3 backdrop-blur-md"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-purple-200">
                  <Users className="w-5 h-5 text-purple-400 animate-bounce" />
                  <h4 className="text-xs font-bold uppercase tracking-wider">Multiple People Detected ({peopleCount})</h4>
                </div>
                <span className="text-[11px] text-purple-300 font-mono">Select person to analyze</span>
              </div>

              <div className="flex flex-wrap gap-3 pt-1">
                {Array.from({ length: peopleCount }).map((_, idx) => (
                  <button
                    key={idx}
                    disabled={reloadingPerson}
                    onClick={() => onSelectPerson && onSelectPerson(idx)}
                    className={`px-5 py-2.5 rounded-2xl text-xs font-bold flex items-center gap-2.5 transition-all border ${selectedPersonIndex === idx
                        ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-400 shadow-lg shadow-purple-500/40 scale-105"
                        : "bg-white/5 hover:bg-white/10 text-white/80 border-white/10 hover:border-white/20"
                      }`}
                  >
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono ${selectedPersonIndex === idx ? 'bg-white text-purple-900 font-bold' : 'bg-white/20 text-white'}`}>
                      {idx + 1}
                    </div>
                    <span>Person {idx + 1}</span>
                    {selectedPersonIndex === idx && <CheckCircle2 className="w-4 h-4 text-emerald-300" />}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white/5 p-4 rounded-2xl border border-white/10 space-y-1 hover:border-purple-500/30 transition-colors">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Skin Tone</span>
              <p className="text-lg font-extrabold text-white tracking-tight">{skinTone}</p>
              <p className="text-[11px] font-mono text-purple-300">ITA Angle: {itaAngle}°</p>
            </div>

            <div className="bg-white/5 p-4 rounded-2xl border border-white/10 space-y-1 hover:border-purple-500/30 transition-colors">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Undertone</span>
              <div className="pt-0.5">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${undertone.includes("Warm") ? "bg-amber-500/20 text-amber-300 border-amber-500/30" :
                    undertone.includes("Cool") ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/30" :
                      "bg-purple-500/20 text-purple-300 border-purple-500/30"
                  }`}>
                  <Flame className="w-3.5 h-3.5" />
                  {undertone}
                </span>
              </div>
              <p className="text-[11px] text-white/40">Lab Chromaticity $a^*, b^*$ ratio</p>
            </div>

            <div className="bg-white/5 p-4 rounded-2xl border border-white/10 space-y-1 hover:border-purple-500/30 transition-colors">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Sampled Skin Color</span>
              <div className="flex items-center gap-3 pt-0.5">
                <div
                  className="w-7 h-7 rounded-full border border-white/30 shadow-md shrink-0"
                  style={{ backgroundColor: `rgb(${avgRgb.join(",")})` }}
                />
                <span className="text-xs font-mono text-white font-semibold">RGB({avgRgb.join(", ")})</span>
              </div>
              <p className="text-[11px] text-white/40">Cheeks & forehead landmarks</p>
            </div>

            <div className="bg-white/5 p-4 rounded-2xl border border-white/10 space-y-1 hover:border-purple-500/30 transition-colors">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider flex items-center gap-1">
                <Info className="w-3 h-3 text-purple-400" /> Evidence Source
              </span>
              <p className="text-xs text-white/80 line-clamp-2 leading-relaxed">{evidence}</p>
            </div>
          </div>

          {/* Lighting or Confidence Notes */}
          {(lightingNote || confidenceNote) && (
            <div className="flex flex-col sm:flex-row gap-3">
              {lightingNote && (
                <div className="bg-amber-500/10 border border-amber-500/30 px-4 py-2.5 rounded-2xl text-xs text-amber-300 flex items-center gap-2.5">
                  <Sun className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>{lightingNote}</span>
                </div>
              )}
              {confidenceNote && (
                <div className="bg-blue-500/10 border border-blue-500/30 px-4 py-2.5 rounded-2xl text-xs text-blue-300 flex items-center gap-2.5">
                  <Info className="w-4 h-4 text-blue-400 shrink-0" />
                  <span>{confidenceNote}</span>
                </div>
              )}
            </div>
          )}

          {/* Existing Outfit & Skin Undertone Harmony Banner */}
          {existingHarmony && (
            <div className="bg-gradient-to-r from-purple-900/40 via-pink-900/30 to-purple-950/40 p-5 rounded-3xl border border-purple-500/30 space-y-2 backdrop-blur-md">
              <div className="flex items-center gap-2 text-purple-200">
                <Shirt className="w-5 h-5 text-pink-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider">Worn Outfit & Skin Undertone Harmony</h3>
              </div>
              <p className="text-sm text-white/95 leading-relaxed font-sans">{existingHarmony}</p>
            </div>
          )}

          {/* Navigation Tabs */}
          <div className="space-y-6 pt-2">
            <div className="flex items-center justify-between border-b border-white/10 pb-4 overflow-x-auto">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab("palette")}
                  className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all flex items-center gap-2 border ${activeTab === "palette"
                      ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-400 shadow-lg shadow-purple-500/30"
                      : "bg-white/5 hover:bg-white/10 text-white/60 border-white/5"
                    }`}
                >
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Top 5 Recommended Colors ({recommendedColors.length})</span>
                </button>

                <button
                  onClick={() => setActiveTab("outfits")}
                  className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all flex items-center gap-2 border ${activeTab === "outfits"
                      ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-400 shadow-lg shadow-purple-500/30"
                      : "bg-white/5 hover:bg-white/10 text-white/60 border-white/5"
                    }`}
                >
                  <Layers className="w-4 h-4 text-pink-400" />
                  <span>Best Outfit Color Combos ({outfitCombos.length})</span>
                </button>

                <button
                  onClick={() => setActiveTab("experiments")}
                  className={`px-5 py-2.5 rounded-full text-xs font-bold transition-all flex items-center gap-2 border ${activeTab === "experiments"
                      ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-400 shadow-lg shadow-purple-500/30"
                      : "bg-white/5 hover:bg-white/10 text-white/60 border-white/5"
                    }`}
                >
                  <Sliders className="w-4 h-4 text-purple-300" />
                  <span>Colors to Experiment ({experimentalColors.length})</span>
                </button>
              </div>
            </div>

            {/* TAB 1: TOP 5 RECOMMENDED COLORS */}
            {activeTab === "palette" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-amber-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Top 5 Recommended Colors for Your {undertone} Undertone</h3>
                  </div>
                  <span className="text-[11px] text-white/50 font-mono">Click any color to inspect & see pairings</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  {recommendedColors.map((color, idx) => (
                    <motion.div
                      key={idx}
                      whileHover={{ y: -4, scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedColorForModal(color)}
                      className="bg-white/5 hover:bg-white/10 p-4 rounded-3xl border border-white/10 hover:border-purple-500/50 transition-all cursor-pointer flex flex-col justify-between space-y-3 group shadow-lg relative overflow-hidden"
                    >
                      {/* Top Rank Badge */}
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono font-extrabold px-2.5 py-0.5 rounded-full bg-gradient-to-r from-purple-500/30 to-pink-500/30 text-purple-200 border border-purple-400/30">
                          {rankLabels[idx] || `#${idx + 1}`}
                        </span>
                        <Maximize2 className="w-3.5 h-3.5 text-white/40 group-hover:text-purple-300 transition-colors" />
                      </div>

                      {/* Live Swatch */}
                      <div className="space-y-2">
                        <div
                          className="w-full h-24 rounded-2xl border-2 border-white/20 shadow-lg relative overflow-hidden flex items-end justify-end p-2 transition-transform duration-300 group-hover:scale-105"
                          style={{ backgroundColor: color.hex, boxShadow: `0 0 20px ${color.hex}44` }}
                        >
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-black/70 backdrop-blur-md text-white border border-white/20">
                            {color.hex}
                          </span>
                        </div>

                        <div>
                          <h4 className="text-base font-extrabold text-white flex items-center justify-between">
                            <span>{color.name}</span>
                          </h4>
                          <p className="text-[10px] font-mono text-white/40">
                            RGB: {color.rgb ? color.rgb.join(", ") : "N/A"}
                          </p>
                        </div>
                      </div>

                      {/* Why it works snippet */}
                      <p className="text-xs text-white/75 line-clamp-2 leading-relaxed italic border-t border-white/5 pt-2">
                        "{color.why_it_works}"
                      </p>

                      {/* Color Pairing Dots Preview */}
                      {color.best_pairings && color.best_pairings.length > 0 && (
                        <div className="pt-1 border-t border-white/5 flex items-center justify-between text-[10px] text-white/50 font-mono">
                          <span>Pairs with:</span>
                          <div className="flex items-center gap-1">
                            {color.best_pairings.map((p, pIdx) => (
                              <div
                                key={pIdx}
                                className="w-3.5 h-3.5 rounded-full border border-white/40 shadow-sm"
                                style={{ backgroundColor: p.hex }}
                                title={p.name}
                              />
                            ))}
                          </div>
                        </div>
                      )}

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedColorForModal(color);
                        }}
                        className="w-full py-1.5 bg-purple-600/30 hover:bg-purple-600 text-purple-200 hover:text-white rounded-xl text-xs font-bold transition-colors flex items-center justify-center gap-1.5 border border-purple-500/30"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>See Color Details</span>
                      </button>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 2: BEST OUTFIT COLOR COMBINATIONS */}
            {activeTab === "outfits" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-5 h-5 text-pink-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Harmonized Outfit Color Combinations</h3>
                  </div>
                  <span className="text-[11px] text-white/50 font-mono">Click color pills to inspect details</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {outfitCombos.map((combo, idx) => (
                    <motion.div
                      key={idx}
                      whileHover={{ y: -3 }}
                      className="bg-white/5 p-6 rounded-3xl border border-white/10 space-y-4 hover:border-purple-500/40 transition-all shadow-xl"
                    >
                      <div className="flex items-center justify-between border-b border-white/10 pb-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-purple-500/20 text-purple-300 flex items-center justify-center font-mono font-bold text-xs border border-purple-500/30">
                            {idx + 1}
                          </div>
                          <span className="text-xs font-extrabold text-white font-mono uppercase tracking-wider">
                            {combo.title}
                          </span>
                          {combo.tag && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                              {combo.tag}
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/20 font-mono font-bold">
                          {combo.harmony_score ? `${combo.harmony_score}% Match` : "Harmonized"}
                        </span>
                      </div>

                      {/* Items List with Interactive Color Pills */}
                      <div className="space-y-2.5 text-xs text-white/80 font-sans">
                        {/* Top Piece */}
                        <div className="flex items-center justify-between bg-white/5 px-3.5 py-2.5 rounded-2xl border border-white/5">
                          <span className="text-white/40 font-medium flex items-center gap-1.5">
                            <Shirt className="w-3.5 h-3.5 text-purple-400" /> Upper Garment:
                          </span>
                          <div className="flex items-center gap-2">
                            {combo.top_hex && (
                              <button
                                onClick={() => setSelectedColorForModal({ name: combo.top, hex: combo.top_hex!, rgb: [100, 100, 100], why_it_works: combo.description })}
                                className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-black/40 border border-white/20 text-[11px] font-mono hover:border-purple-400 transition-colors"
                              >
                                <div className="w-3 h-3 rounded-full border border-white/50" style={{ backgroundColor: combo.top_hex }} />
                                <span className="text-white font-semibold">{combo.top_hex}</span>
                              </button>
                            )}
                            <span className="font-bold text-white">{combo.top}</span>
                          </div>
                        </div>

                        {/* Bottom Piece */}
                        <div className="flex items-center justify-between bg-white/5 px-3.5 py-2.5 rounded-2xl border border-white/5">
                          <span className="text-white/40 font-medium flex items-center gap-1.5">
                            <Layers className="w-3.5 h-3.5 text-blue-400" /> Lower Garment:
                          </span>
                          <div className="flex items-center gap-2">
                            {combo.bottom_hex && (
                              <button
                                onClick={() => setSelectedColorForModal({ name: combo.bottom, hex: combo.bottom_hex!, rgb: [100, 100, 100], why_it_works: combo.description })}
                                className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-black/40 border border-white/20 text-[11px] font-mono hover:border-purple-400 transition-colors"
                              >
                                <div className="w-3 h-3 rounded-full border border-white/50" style={{ backgroundColor: combo.bottom_hex }} />
                                <span className="text-white font-semibold">{combo.bottom_hex}</span>
                              </button>
                            )}
                            <span className="font-bold text-white">{combo.bottom}</span>
                          </div>
                        </div>

                        {/* Shoes */}
                        <div className="flex items-center justify-between bg-white/5 px-3.5 py-2.5 rounded-2xl border border-white/5">
                          <span className="text-white/40 font-medium flex items-center gap-1.5">
                            <Compass className="w-3.5 h-3.5 text-pink-400" /> Footwear:
                          </span>
                          <div className="flex items-center gap-2">
                            {combo.shoes_hex && (
                              <button
                                onClick={() => setSelectedColorForModal({ name: combo.shoes, hex: combo.shoes_hex!, rgb: [100, 100, 100], why_it_works: combo.description })}
                                className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-black/40 border border-white/20 text-[11px] font-mono hover:border-purple-400 transition-colors"
                              >
                                <div className="w-3 h-3 rounded-full border border-white/50" style={{ backgroundColor: combo.shoes_hex }} />
                                <span className="text-white font-semibold">{combo.shoes_hex}</span>
                              </button>
                            )}
                            <span className="font-bold text-white">{combo.shoes}</span>
                          </div>
                        </div>
                      </div>

                      <p className="text-xs text-white/75 leading-relaxed italic bg-white/5 p-3.5 rounded-2xl border border-white/5">
                        "{combo.description}"
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: COLORS TO EXPERIMENT WITH */}
            {activeTab === "experiments" && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-purple-300" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Colors to Experiment With (Low Judgment Styling)</h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {experimentalColors.map((color, idx) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedColorForModal(color)}
                      className="bg-white/5 p-5 rounded-3xl border border-white/10 space-y-3 flex flex-col justify-between hover:border-purple-500/30 transition-colors cursor-pointer"
                    >
                      <div className="space-y-2.5">
                        <div
                          className="w-full h-16 rounded-2xl border border-white/20 shadow-sm relative overflow-hidden flex items-end justify-end p-2"
                          style={{ backgroundColor: color.hex }}
                        >
                          <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-black/60 backdrop-blur-md text-white">
                            {color.hex}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-bold text-white">{color.name}</h4>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(color.hex, color.name);
                            }}
                            className="text-[10px] text-white/40 hover:text-white flex items-center gap-1 font-mono"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <p className="text-[10px] font-mono text-white/40">
                          RGB: {color.rgb ? color.rgb.join(", ") : "N/A"}
                        </p>
                      </div>

                      <p className="text-xs text-white/70 italic leading-relaxed border-t border-white/5 pt-2">
                        {color.experiment_note}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* INTERACTIVE "SEE COLOR DETAILS & STYLING INSPECTOR" MODAL */}
      <AnimatePresence>
        {selectedColorForModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-[#0f0a1c] border border-purple-500/40 p-6 md:p-8 rounded-[2.5rem] max-w-2xl w-full shadow-2xl space-y-6 relative overflow-hidden text-white"
            >
              {/* Top Modal Controls */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white">
                    <Palette className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-xl font-extrabold text-white">Color Visualizer & Inspector</h3>
                    <p className="text-xs text-white/50">Comprehensive specs, contrast test & color pairing analysis</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedColorForModal(null)}
                  className="p-2 bg-white/10 hover:bg-white/20 rounded-full text-white/80 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Main Swatch & Fabric Contrast Preview */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-white/60">
                  <span>Fabric Canvas Preview:</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setModalBgMode("dark")}
                      className={`px-3 py-1 rounded-full text-[11px] font-bold flex items-center gap-1.5 border transition-all ${modalBgMode === "dark" ? "bg-purple-600 text-white border-purple-400" : "bg-white/5 text-white/50 border-white/10"
                        }`}
                    >
                      <Moon className="w-3 h-3" /> Evening (Dark)
                    </button>
                    <button
                      onClick={() => setModalBgMode("light")}
                      className={`px-3 py-1 rounded-full text-[11px] font-bold flex items-center gap-1.5 border transition-all ${modalBgMode === "light" ? "bg-purple-600 text-white border-purple-400" : "bg-white/5 text-white/50 border-white/10"
                        }`}
                    >
                      <SunMedium className="w-3 h-3" /> Daytime (Light)
                    </button>
                  </div>
                </div>

                <div
                  className={`w-full h-44 rounded-3xl border-2 border-white/20 shadow-2xl flex flex-col justify-between p-5 relative transition-colors duration-500 ${modalBgMode === "light" ? "bg-slate-100 text-slate-900" : "bg-slate-950 text-white"
                    }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] uppercase font-mono font-bold tracking-widest px-2.5 py-1 rounded-full bg-black/60 text-white border border-white/20">
                        {undertone} Undertone Match
                      </span>
                    </div>
                    <button
                      onClick={() => copyToClipboard(selectedColorForModal.hex, selectedColorForModal.name)}
                      className="px-3 py-1.5 bg-black/70 hover:bg-black text-white rounded-xl text-xs font-mono font-bold flex items-center gap-1.5 border border-white/20 transition-all shadow-md"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      <span>{selectedColorForModal.hex}</span>
                    </button>
                  </div>

                  <div className="flex items-center gap-4">
                    <div
                      className="w-16 h-16 rounded-2xl border-2 border-white shadow-2xl shrink-0"
                      style={{ backgroundColor: selectedColorForModal.hex, boxShadow: `0 0 25px ${selectedColorForModal.hex}88` }}
                    />
                    <div>
                      <h2 className={`text-2xl font-black ${modalBgMode === 'light' ? 'text-slate-900' : 'text-white'}`}>
                        {selectedColorForModal.name}
                      </h2>
                      <p className={`text-xs font-mono ${modalBgMode === 'light' ? 'text-slate-600' : 'text-white/60'}`}>
                        RGB: {selectedColorForModal.rgb ? selectedColorForModal.rgb.join(", ") : "N/A"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Technical Specifications Grid */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-white/5 p-3 rounded-2xl border border-white/10 text-center space-y-1">
                  <span className="text-[10px] text-white/40 font-mono uppercase">HEX Code</span>
                  <p className="text-sm font-mono font-bold text-purple-300">{selectedColorForModal.hex}</p>
                </div>
                <div className="bg-white/5 p-3 rounded-2xl border border-white/10 text-center space-y-1">
                  <span className="text-[10px] text-white/40 font-mono uppercase">RGB Spectrum</span>
                  <p className="text-sm font-mono font-bold text-pink-300">{selectedColorForModal.rgb ? selectedColorForModal.rgb.join(", ") : "N/A"}</p>
                </div>
                <div className="bg-white/5 p-3 rounded-2xl border border-white/10 text-center space-y-1">
                  <span className="text-[10px] text-white/40 font-mono uppercase">HSL Representation</span>
                  <p className="text-sm font-mono font-bold text-amber-300">{getHslString(selectedColorForModal.rgb)}</p>
                </div>
              </div>

              {/* Best Color Pairings Strip */}
              {selectedColorForModal.best_pairings && selectedColorForModal.best_pairings.length > 0 && (
                <div className="space-y-2.5 bg-white/5 p-4 rounded-2xl border border-white/10">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-pink-400" /> Recommended Color Pairings
                  </h4>
                  <div className="grid grid-cols-3 gap-2.5">
                    {selectedColorForModal.best_pairings.map((pairing, pIdx) => (
                      <div
                        key={pIdx}
                        className="bg-black/40 p-2.5 rounded-xl border border-white/10 flex items-center gap-2.5"
                      >
                        <div
                          className="w-6 h-6 rounded-full border border-white/30 shrink-0"
                          style={{ backgroundColor: pairing.hex }}
                        />
                        <div className="overflow-hidden">
                          <p className="text-xs font-bold text-white truncate">{pairing.name}</p>
                          <p className="text-[10px] font-mono text-white/40">{pairing.hex}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Why it works & Occasion tips */}
              <div className="space-y-3">
                {selectedColorForModal.why_it_works && (
                  <div className="bg-purple-900/30 p-4 rounded-2xl border border-purple-500/30 space-y-1">
                    <h4 className="text-xs font-bold text-purple-200 uppercase tracking-wider flex items-center gap-1.5">
                      <Check className="w-4 h-4 text-emerald-400" /> Why It Flatters Your Skin
                    </h4>
                    <p className="text-xs text-white/90 leading-relaxed font-sans">{selectedColorForModal.why_it_works}</p>
                  </div>
                )}

                {selectedColorForModal.occasion_tip && (
                  <div className="bg-pink-950/30 p-4 rounded-2xl border border-pink-500/30 space-y-1">
                    <h4 className="text-xs font-bold text-pink-200 uppercase tracking-wider flex items-center gap-1.5">
                      <Shirt className="w-4 h-4 text-pink-400" /> Occasion & Outfit Styling Advice
                    </h4>
                    <p className="text-xs text-white/90 leading-relaxed font-sans">{selectedColorForModal.occasion_tip}</p>
                  </div>
                )}

                {selectedColorForModal.experiment_note && (
                  <div className="bg-amber-950/30 p-4 rounded-2xl border border-amber-500/30 space-y-1">
                    <h4 className="text-xs font-bold text-amber-200 uppercase tracking-wider flex items-center gap-1.5">
                      <Sliders className="w-4 h-4 text-amber-400" /> Experimentation Styling Note
                    </h4>
                    <p className="text-xs text-white/90 leading-relaxed font-sans">{selectedColorForModal.experiment_note}</p>
                  </div>
                )}
              </div>

              {/* Footer Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => copyToClipboard(selectedColorForModal.hex, selectedColorForModal.name)}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-2xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-600/30 text-xs"
                >
                  <Copy className="w-4 h-4" />
                  <span>Copy HEX Code ({selectedColorForModal.hex})</span>
                </button>
                <button
                  onClick={() => setSelectedColorForModal(null)}
                  className="py-3 px-6 bg-white/10 hover:bg-white/20 text-white rounded-2xl text-xs font-bold transition-colors border border-white/10"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};
