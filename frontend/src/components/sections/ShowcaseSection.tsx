import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react"
import { Button } from "../ui/button"

const items = [
  {
    id: 1,
    before: "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=1000&auto=format&fit=crop",
    after: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop",
    style: "Streetwear Chic"
  },
  {
    id: 2,
    before: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
    after: "https://images.unsplash.com/photo-1550614000-4b95d466f270?q=80&w=1000&auto=format&fit=crop",
    style: "Formal Elegance"
  },
  {
    id: 3,
    before: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=1000&auto=format&fit=crop",
    after: "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000&auto=format&fit=crop",
    style: "Smart Casual"
  }
]

export function ShowcaseSection() {
  const [currentIndex, setCurrentIndex] = useState(0)

  const next = () => setCurrentIndex((prev) => (prev + 1) % items.length)
  const prev = () => setCurrentIndex((prev) => (prev - 1 + items.length) % items.length)

  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Virtual <span className="text-gradient">Try-On</span>
          </h2>
          <p className="text-white/60 max-w-2xl mx-auto text-lg">
            Experience photorealistic outfit generation in milliseconds.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto glass-card rounded-[2.5rem] p-4 md:p-8">
          <div className="relative aspect-[4/3] md:aspect-[21/9] rounded-3xl overflow-hidden group">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentIndex}
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                className="absolute inset-0 flex"
              >
                {/* Before Image */}
                <div className="w-1/2 relative h-full">
                  <img src={items[currentIndex].before} alt="Before" className="w-full h-full object-cover" />
                  <div className="absolute top-4 left-4 glass-card px-3 py-1 rounded-full text-xs font-medium text-white/80">
                    Before
                  </div>
                </div>
                {/* After Image */}
                <div className="w-1/2 relative h-full">
                  <img src={items[currentIndex].after} alt="After" className="w-full h-full object-cover" />
                  <div className="absolute top-4 right-4 glass-card px-3 py-1 rounded-full text-xs font-medium text-white/80 border-purple-500/30 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-purple-400" /> After
                  </div>
                </div>

                {/* Center Divider Line */}
                <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-white/20 shadow-[0_0_15px_rgba(255,255,255,0.5)] -translate-x-1/2 z-10">
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white flex items-center justify-center text-black">
                    <Sparkles className="w-4 h-4" />
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Overlay Gradient */}
            <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/80 to-transparent z-20" />

            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-30 text-center">
              <span className="text-white text-lg md:text-xl font-medium tracking-wide">
                {items[currentIndex].style}
              </span>
            </div>
          </div>

          {/* Controls */}
          <div className="absolute top-1/2 -left-4 md:-left-6 -translate-y-1/2 z-40">
            <Button variant="outline" size="icon" className="rounded-full bg-black/50 backdrop-blur-md border-white/10 hover:bg-white/10" onClick={prev}>
              <ChevronLeft className="w-5 h-5 text-white" />
            </Button>
          </div>
          <div className="absolute top-1/2 -right-4 md:-right-6 -translate-y-1/2 z-40">
            <Button variant="outline" size="icon" className="rounded-full bg-black/50 backdrop-blur-md border-white/10 hover:bg-white/10" onClick={next}>
              <ChevronRight className="w-5 h-5 text-white" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
