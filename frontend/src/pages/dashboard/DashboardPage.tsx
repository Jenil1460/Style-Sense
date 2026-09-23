import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Activity, Camera, TrendingUp } from "lucide-react"
import { MetricCard } from "../../components/dashboard/MetricCard"
import { UploadCard } from "../../components/dashboard/UploadCard"
import { InsightsCharts } from "../../components/dashboard/InsightsCharts"
import { useAuth } from "../../context/AuthContext"
import { api } from "../../lib/api"
import toast from "react-hot-toast"

export function DashboardPage() {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const response = await api.get('/ai/history');
      setAnalyses(response.data || []);
    } catch (error) {
      toast.error("Failed to load dashboard data");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalUploads = analyses.length;
  const averageScore = totalUploads > 0
    ? Math.round(analyses.reduce((acc, curr) => acc + curr.fashion_score, 0) / totalUploads)
    : 0;


  return (
    <div className="max-w-7xl mx-auto space-y-8">

      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 tracking-tight">Welcome back, {user?.first_name || 'User'}.</h1>
          <p className="text-white/50 text-lg">Your AI stylist is ready to analyze your next outfit.</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-2 w-fit backdrop-blur-md"
        >
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm font-medium text-white/80">AI Engine Online</span>
        </motion.div>
      </div>

      {/* Metrics Row */}
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
          title="Outfits Analyzed"
          value={totalUploads.toString()}
          icon={Camera}
          trend={totalUploads > 0 ? "Total" : ""}
          trendUp={true}
          delay={0.2}
        />
        <MetricCard
          title="Top Style"
          value={user?.preferred_styles?.[0] || 'Minimalist'}
          icon={TrendingUp}
          delay={0.3}
        />
      </div>

      {/* Main Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <UploadCard onUploadComplete={fetchData} />
      </motion.div>

      {/* Insights & Charts */}
      <div className="pt-4">
        <InsightsCharts analyses={analyses} />
      </div>

      {/* Recent Uploads */}
      <div className="pt-4">
        <h2 className="text-2xl font-bold text-white mb-4">Recent Uploads</h2>
        <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory hide-scrollbar">
          {analyses.length > 0 ? analyses.slice(0, 5).map((item) => (
            <div key={item.id} className="min-w-[150px] aspect-[3/4] rounded-2xl overflow-hidden glass-card snap-start relative group cursor-pointer border-white/5">
              <img
                src={item.image_url}
                alt={`Upload`}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center">
                <span className="text-white font-bold text-lg">{item.fashion_score}%</span>
                <span className="text-white/70 text-xs">Score</span>
              </div>
            </div>
          )) : (
            <div className="text-white/40 text-sm italic">No recent uploads.</div>
          )}
        </div>
      </div>
    </div>
  )
}
