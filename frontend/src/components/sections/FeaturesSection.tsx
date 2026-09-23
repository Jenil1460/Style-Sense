import { motion } from "framer-motion"
import { ScanFace, Shirt, Star, Palette, Inbox, Calendar, TrendingUp, History } from "lucide-react"

const features = [
  { icon: ScanFace, title: "Computer Vision", desc: "Advanced body type and posture analysis." },
  { icon: Shirt, title: "Virtual Try-On", desc: "See clothes on yourself before you buy." },
  { icon: Star, title: "AI Fashion Score", desc: "Real-time feedback on your outfit combinations." },
  { icon: Palette, title: "Color Analysis", desc: "Discover colors that complement your skin tone." },
  { icon: Inbox, title: "Wardrobe AI", desc: "Digitize and manage your entire closet smartly." },
  { icon: Calendar, title: "Occasion Recommendations", desc: "Perfect outfits for every event." },
  { icon: TrendingUp, title: "Trend Detection", desc: "Stay ahead with AI-spotted global fashion trends." },
  { icon: History, title: "Fashion History", desc: "Learn from iconic styles tailored to your taste." },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    }
  }
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
}

export function FeaturesSection() {
  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Next-Gen <span className="text-gradient">Capabilities</span>
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto text-lg">
            Powered by state-of-the-art machine learning models designed exclusively for fashion.
          </p>
        </div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={index}
                variants={cardVariants}
                className="group p-6 rounded-3xl glass-card hover:bg-white/5 transition-colors duration-300 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative z-10">
                  <div className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center mb-6 border border-white/5 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-white/60 text-sm leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
