import { motion } from "framer-motion"
import { Star } from "lucide-react"

const testimonials = [
  {
    name: "Elena R.",
    role: "Fashion Blogger",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150&auto=format&fit=crop",
    content: "StyleSense AI completely transformed how I put together my daily outfits. The virtual try-on is scarily accurate, and it saves me so much time in the morning.",
  },
  {
    name: "James T.",
    role: "Creative Director",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=150&auto=format&fit=crop",
    content: "As someone in the industry, I was skeptical. But the AI's understanding of fit, color theory, and current trends is genuinely mind-blowing. It's like having a personal stylist in your pocket.",
  },
  {
    name: "Sophia L.",
    role: "Tech Executive",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?q=80&w=150&auto=format&fit=crop",
    content: "I needed a wardrobe overhaul but didn't have the time to shop. This app analyzed my style and recommended a capsule wardrobe that I absolutely love. Worth every penny.",
  }
]

export function TestimonialsSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-500/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Loved by <span className="text-gradient">Trendsetters</span>
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto text-lg">
            See what our users are saying about the future of fashion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ delay: index * 0.2, duration: 0.6 }}
              className="glass-card p-8 rounded-3xl relative group hover:-translate-y-2 transition-transform duration-300"
            >
              <div className="flex items-center gap-1 mb-6">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-white text-white" />
                ))}
              </div>
              <p className="text-white/80 text-lg leading-relaxed mb-8">
                "{testimonial.content}"
              </p>
              <div className="flex items-center gap-4 mt-auto">
                <img
                  src={testimonial.avatar}
                  alt={testimonial.name}
                  className="w-14 h-14 rounded-full object-cover border-2 border-white/10"
                />
                <div>
                  <h4 className="text-white font-medium">{testimonial.name}</h4>
                  <span className="text-white/50 text-sm">{testimonial.role}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
