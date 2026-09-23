import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Trash2, RotateCcw } from "lucide-react";
import { api } from "../../lib/api";
import { extractErrorMessage } from "../../lib/utils";
import toast from "react-hot-toast";


export function HistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/ai/history');
      setItems(response.data || []);
    } catch (error) {
      toast.error("Failed to fetch history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (item: any) => {
    try {
      const targetId = item.id || item.upload_id;
      if (!targetId) return;

      if (item.id) {
        await api.delete(`/ai/analysis/${item.id}`);
      } else if (item.upload_id) {
        await api.delete(`/uploads/${item.upload_id}`);
      }
      toast.success("Item deleted from Cloudinary & Database.");
      setItems(prev => prev.filter(i => i.id !== item.id && i.upload_id !== item.upload_id));
    } catch (error: any) {
      console.error("Delete error:", error);
      toast.error(extractErrorMessage(error, "Failed to delete item"));
    }
  };



  if (loading) {
    return (
      <div className="flex h-full items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col h-full items-center justify-center text-center max-w-md mx-auto space-y-4 min-h-[400px]">
        <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center">
          <RotateCcw className="w-10 h-10 text-white/20" />
        </div>
        <h2 className="text-2xl font-bold text-white">No history yet</h2>
        <p className="text-white/50">Upload an outfit on the dashboard to start generating your style history.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">History</h1>
        <p className="text-white/50">Your past AI analyses and style scores.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {items.map((item) => (
          <div key={item.id} className="aspect-[3/4] rounded-2xl overflow-hidden glass-card border-white/5 relative group">
            <img
              src={item.image_url}
              alt="Upload"
              className="w-full h-full object-cover"
            />

            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-100 transition-opacity">
              <div className="absolute bottom-0 left-0 right-0 p-4">
                <div className="flex justify-between items-end">
                  <div>
                    <div className="text-purple-400 font-bold text-2xl">{item.fashion_score}<span className="text-sm text-white/50">/100</span></div>
                    <div className="text-white/50 text-xs mt-1">{new Date(item.created_at).toLocaleDateString()}</div>
                  </div>

                  <button
                    onClick={() => navigate(`/dashboard/results/${item.id}`)}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-full text-white text-sm backdrop-blur-md transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>

            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => handleDelete(item)}
                className="w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white/70 hover:text-red-400 hover:bg-black backdrop-blur-md"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
