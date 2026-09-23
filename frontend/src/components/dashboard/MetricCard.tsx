import { motion } from "framer-motion"
import type { LucideIcon } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: string
  trendUp?: boolean
  delay?: number
}

export function MetricCard({ title, value, icon: Icon, trend, trendUp, delay = 0 }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass-card rounded-2xl p-6 border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors"
    >
      <div className="flex items-start justify-between mb-4 relative z-10">
        <div className="p-2.5 rounded-xl bg-white/5 group-hover:bg-white/10 transition-colors">
          <Icon className="w-5 h-5 text-white/70 group-hover:text-white" />
        </div>
        {trend && (
          <div className={`text-xs font-medium px-2 py-1 rounded-full ${trendUp ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'}`}>
            {trend}
          </div>
        )}
      </div>
      <div className="relative z-10">
        <h3 className="text-3xl font-bold text-white mb-1 tracking-tight">{value}</h3>
        <p className="text-sm text-white/50">{title}</p>
      </div>

      {/* Subtle background glow on hover */}
      <div className="absolute -bottom-12 -right-12 w-32 h-32 bg-white/5 rounded-full blur-2xl group-hover:bg-white/10 transition-colors pointer-events-none" />
    </motion.div>
  )
}
