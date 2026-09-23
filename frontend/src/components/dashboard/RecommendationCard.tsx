import { motion } from "framer-motion"
import { Heart, Download, Share2, Sparkles } from "lucide-react"

interface RecommendationCardProps {
  image: string
  occasion: string
  confidence: number
  styleMatch: number
  insights: string
  delay?: number
}

export function RecommendationCard({ image, occasion, confidence, styleMatch, insights, delay = 0 }: RecommendationCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="glass-card rounded-[2rem] overflow-hidden border-white/5 flex flex-col group"
    >
      <div className="relative aspect-[4/5] overflow-hidden">
        <img 
          src={image} 
          alt="Outfit recommendation" 
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-black/30" />
        
        {/* Top Badges */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
          <div className="glass-card bg-black/40 px-3 py-1.5 rounded-full text-xs font-medium text-white border-white/10 backdrop-blur-md">
            {occasion}
          </div>
          <div className="flex flex-col gap-2">
            <button className="w-9 h-9 rounded-full glass-card bg-black/40 flex items-center justify-center text-white/70 hover:text-white hover:bg-white/20 transition-all border-white/10">
              <Heart className="w-4 h-4" />
            </button>
            <button className="w-9 h-9 rounded-full glass-card bg-black/40 flex items-center justify-center text-white/70 hover:text-white hover:bg-white/20 transition-all border-white/10">
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Stats overlays */}
        <div className="absolute bottom-4 left-4 right-4 flex gap-2">
          <div className="flex-1 glass-card bg-black/50 backdrop-blur-md border-white/10 p-2.5 rounded-2xl">
            <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">Style Match</div>
            <div className="text-lg font-bold text-white leading-none">{styleMatch}%</div>
            <div className="w-full bg-white/10 h-1 mt-2 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${styleMatch}%` }} />
            </div>
          </div>
          <div className="flex-1 glass-card bg-black/50 backdrop-blur-md border-white/10 p-2.5 rounded-2xl">
            <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">AI Confidence</div>
            <div className="text-lg font-bold text-white leading-none">{confidence}%</div>
            <div className="w-full bg-white/10 h-1 mt-2 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${confidence}%` }} />
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 flex flex-col flex-1">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <h4 className="font-semibold text-white">AI Style Insights</h4>
        </div>
        <p className="text-white/60 text-sm leading-relaxed mb-6 flex-1">
          {insights}
        </p>
        
        <button className="w-full flex items-center justify-center gap-2 bg-white text-black py-3 rounded-xl font-medium text-sm hover:bg-white/90 transition-colors">
          <Download className="w-4 h-4" />
          Save Lookbook
        </button>
      </div>
    </motion.div>
  )
}
