import { useState, useEffect } from "react";
import { Loader2, TrendingUp, Activity, Star } from "lucide-react";
import { api } from "../../lib/api";
import { MetricCard } from "../../components/dashboard/MetricCard";
import { InsightsCharts } from "../../components/dashboard/InsightsCharts";

export function StatisticsPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/ai/history');
        setAnalyses(response.data || []);
      } catch (error) {
        console.error("Failed to load statistics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const totalUploads = analyses.length;
  const averageScore = totalUploads > 0
    ? Math.round(analyses.reduce((acc, curr) => acc + curr.fashion_score, 0) / totalUploads)
    : 0;

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Statistics</h1>
        <p className="text-white/50">Track your fashion score and upload activity over time.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Average Style Score"
          value={averageScore > 0 ? averageScore.toString() : "-"}
          icon={Activity}
          trend={totalUploads > 0 ? "All time" : ""}
          trendUp={true}
          delay={0.1}
        />
        <MetricCard
          title="Outfits Uploaded"
          value={totalUploads.toString()}
          icon={TrendingUp}
          trend={totalUploads > 0 ? "Total" : ""}
          trendUp={true}
          delay={0.2}
        />
        <MetricCard
          title="AI Analyses"
          value={totalUploads.toString()}
          icon={Star}
          delay={0.3}
        />
      </div>

      <div className="pt-4">
        <InsightsCharts analyses={analyses} />
      </div>

      <div className="glass-card rounded-3xl p-8 border-white/5 mt-8">
        <h2 className="text-xl font-bold text-white mb-4">Style Evolution</h2>
        <p className="text-white/60 text-sm leading-relaxed">
          {totalUploads > 0
            ? "Your style profile is continuously evolving. Keep uploading more outfits to let the AI learn and refine your personalized fashion recommendations."
            : "Upload an outfit on the dashboard to start generating your style history and unlock AI insights."}
        </p>
      </div>
    </div>
  );
}
