import { useState, useEffect } from "react";
import { Loader2, Shirt, Sparkles, Trash2 } from "lucide-react";
import { api } from "../../lib/api";
import toast from "react-hot-toast";

export function WardrobePage() {
  const [items, setItems] = useState<any[]>([]);
  const [combinations, setCombinations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchWardrobe = async () => {
    try {
      const response = await api.get('/wardrobe');
      setItems(response.data || []);
    } catch (error) {
      toast.error("Failed to load wardrobe");
    } finally {
      setLoading(false);
    }
  };

  const fetchCombinations = async () => {
    setGenerating(true);
    try {
      const resp = await api.get('/wardrobe/combinations');
      setCombinations(resp.data?.combinations || []);
      toast.success("Outfit combinations generated!");
    } catch (err) {
      toast.error("Could not generate combinations.");
    } finally {
      setGenerating(false);
    }
  };

  const handleDeleteItem = async (itemId: string) => {

    try {
      await api.delete(`/wardrobe/${itemId}`);
      setItems(prev => prev.filter(i => i.id !== itemId));
      toast.success("Item removed from wardrobe.");
    } catch (err) {
      toast.error("Failed to delete item.");
    }
  };

  useEffect(() => {
    fetchWardrobe();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Personal Wardrobe</h1>
          <p className="text-white/50">Your saved apparel pieces and AI-generated outfit pairings.</p>
        </div>
        {items.length > 0 && (
          <button
            onClick={fetchCombinations}
            disabled={generating}
            className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-medium rounded-full flex items-center gap-2 transition-all w-fit shadow-lg shadow-purple-500/20"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            <span>Generate Outfit Pairings</span>
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <div className="flex flex-col h-full min-h-[350px] items-center justify-center text-center max-w-md mx-auto space-y-4 glass-card p-8 rounded-3xl border-white/5">
          <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center">
            <Shirt className="w-10 h-10 text-white/20" />
          </div>
          <h2 className="text-2xl font-bold text-white">Your Wardrobe is Empty</h2>
          <p className="text-white/50 text-sm">Save clothing recommendations or try-on previews to build your personalized style wardrobe.</p>
        </div>
      ) : (
        <>
          {/* Wardrobe Items Grid */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Saved Clothes ({items.length})</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {items.map((item) => (
                <div key={item.id} className="glass-card p-3 rounded-2xl border-white/5 space-y-3 group relative">
                  <div className="aspect-[3/4] rounded-xl overflow-hidden bg-black/50 relative">
                    <img
                      src={item.image_url}
                      alt={item.clothing_type}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="absolute top-2 right-2 p-2 bg-black/60 hover:bg-red-500/80 text-white rounded-full transition-colors backdrop-blur-md opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="px-1">
                    <h3 className="text-white font-medium text-sm">{item.clothing_type}</h3>
                    <p className="text-white/50 text-xs">{item.color_name} • {item.category}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Outfit Combinations */}
          {combinations.length > 0 && (
            <div className="space-y-4 pt-6 border-t border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">AI Outfit Pairings</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {combinations.map((comb, i) => (
                  <div key={i} className="glass-card p-5 rounded-3xl border-white/5 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/30">
                        Match Score {comb.match_score}%
                      </span>
                      <span className="text-xs text-white/40">{comb.occasion}</span>
                    </div>
                    <h4 className="text-white font-medium text-sm leading-snug">{comb.title}</h4>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
