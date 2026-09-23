import { motion } from "framer-motion"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from "recharts"

// Custom Tooltip for Line Chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card bg-black/80 backdrop-blur-xl border-white/10 p-3 rounded-xl shadow-2xl">
        <p className="text-white/50 text-xs mb-1">{label}</p>
        <p className="text-white font-bold text-lg">
          Score: <span className="text-purple-400">{payload[0].value}</span>
        </p>
      </div>
    )
  }
  return null
}

export function InsightsCharts({ analyses = [] }: { analyses?: any[] }) {
  // Generate lineData from the last 7 analyses
  const sortedByDate = [...analyses].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  const recent7 = sortedByDate.slice(-7);

  const lineData = recent7.map(a => {
    const d = new Date(a.created_at);
    const day = d.toLocaleDateString('en-US', { weekday: 'short' });
    return { name: day, score: a.fashion_score };
  });

  if (lineData.length === 0) {
    lineData.push({ name: "Today", score: 0 });
  }

  // Generate radarData from styles
  const styleCounts: Record<string, number> = {};
  analyses.forEach(a => {
    if (a.styles) {
      a.styles.forEach((s: any) => {
        styleCounts[s.style_name] = (styleCounts[s.style_name] || 0) + s.confidence * 100;
      });
    }
  });

  const radarData = Object.entries(styleCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([subject, A]) => ({
      subject,
      A: Math.round(A / analyses.length),
      fullMark: 100
    }));

  if (radarData.length === 0) {
    radarData.push({ subject: "Upload first", A: 0, fullMark: 100 });
  }
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

      {/* Evolution Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card rounded-3xl p-6 border-white/5 flex flex-col h-[400px]"
      >
        <div className="mb-6">
          <h3 className="text-lg font-bold text-white">Style Evolution</h3>
          <p className="text-sm text-white/50">Your weekly AI fashion score progression.</p>
        </div>
        <div className="flex-1 w-full relative -left-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
              <defs>
                <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 2 }} />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#a855f7"
                strokeWidth={3}
                dot={{ r: 4, fill: "#050505", stroke: "#a855f7", strokeWidth: 2 }}
                activeDot={{ r: 6, fill: "#a855f7", stroke: "#fff", strokeWidth: 2 }}
                animationDuration={2000}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Radar Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-card rounded-3xl p-6 border-white/5 flex flex-col h-[400px]"
      >
        <div className="mb-2">
          <h3 className="text-lg font-bold text-white">Style Archetype</h3>
          <p className="text-sm text-white/50">Your detected aesthetic distribution.</p>
        </div>
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
              <Radar
                name="Style"
                dataKey="A"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="#3b82f6"
                fillOpacity={0.3}
                animationDuration={2000}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

    </div>
  )
}
