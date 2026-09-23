import { motion } from "framer-motion"
import { Upload, Cpu, Search, Sparkles, Shirt, Download } from "lucide-react"

const steps = [
  { icon: Upload, title: "Upload Photo", desc: "Start with a full-body mirror selfie." },
  { icon: Cpu, title: "AI Analysis", desc: "Our neural net maps your body type and posture." },
  { icon: Search, title: "Style Detection", desc: "Identifying your current aesthetic and vibe." },
  { icon: Sparkles, title: "Recommendations", desc: "Curated options from top designer brands." },
  { icon: Shirt, title: "Virtual Try-On", desc: "Photorealistic rendering of the new fit." },
  { icon: Download, title: "Download", desc: "Save your lookbook and shop the items." },
]

export function HowItWorksSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="container mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            The <span className="text-gradient">Process</span>
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto text-lg">
            Seamless from upload to perfect outfit.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto">
          {/* Connecting Line */}
          <div className="absolute top-1/2 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent hidden lg:block -translate-y-1/2" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8 relative z-10">
            {steps.map((step, index) => {
              const Icon = step.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="flex flex-col items-center text-center group"
                >
                  <div className="w-16 h-16 rounded-2xl glass-card flex items-center justify-center mb-6 relative overflow-hidden transition-transform duration-300 group-hover:-translate-y-2">
                    <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <Icon className="w-6 h-6 text-white group-hover:scale-110 transition-transform duration-300" />
                    {/* Glowing dot for timeline */}
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-[2px] bg-white/50 blur-[2px] opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-sm text-white/50">{step.desc}</p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
