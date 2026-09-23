import { motion } from "framer-motion"
import { Button } from "../ui/button"
import { Play, Sparkles, ScanFace, Palette } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* Background gradients and particles */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[150px]" />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="flex flex-col gap-6"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 w-fit">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium text-white/80">StyleSense AI 2.0 is live</span>
            </div>

            <h1 className="text-5xl lg:text-7xl font-bold tracking-tight text-white leading-[1.1]">
              Style Yourself <br />
              <span className="text-gradient">with AI.</span>
            </h1>

            <p className="text-lg text-white/60 max-w-xl leading-relaxed">
              Your Personal AI Fashion Stylist. Using advanced Computer Vision and Generative AI to analyze your outfit, recommend better styles, and generate realistic virtual try-on previews in seconds.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <Button size="lg" className="gap-2">
                Try Now <ScanFace className="w-4 h-4" />
              </Button>
              <Button size="lg" variant="outline" className="gap-2">
                <Play className="w-4 h-4" /> Watch Demo
              </Button>
            </div>
          </motion.div>

          {/* Right Content - Floating Dashboard */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="relative lg:h-[600px] flex items-center justify-center"
          >
            <div className="relative w-full max-w-md aspect-[4/5] glass-card rounded-3xl overflow-hidden border border-white/10 shadow-[0_0_100px_rgba(255,255,255,0.05)]">
              {/* Dummy Image Background */}
              <div className="absolute inset-0 bg-neutral-900">
                <img
                  src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop"
                  alt="Fashion Model"
                  className="w-full h-full object-cover opacity-60"
                />
              </div>

              {/* Animated Scan Line */}
              <motion.div
                className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent shadow-[0_0_10px_rgba(96,165,250,0.5)] z-20"
                animate={{ top: ["0%", "100%", "0%"] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              />

              {/* Floating UI Elements */}
              <div className="absolute inset-0 p-6 flex flex-col justify-between z-10">
                <div className="flex justify-between items-start">
                  <motion.div
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="glass-card rounded-2xl p-3 flex flex-col gap-1"
                  >
                    <span className="text-xs text-white/60">AI Style Score</span>
                    <div className="flex items-end gap-1">
                      <span className="text-2xl font-bold text-white">98</span>
                      <span className="text-sm text-green-400 mb-1">+2</span>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="glass-card rounded-2xl p-3 flex items-center gap-2"
                  >
                    <Palette className="w-4 h-4 text-white/80" />
                    <div className="flex gap-1">
                      <div className="w-4 h-4 rounded-full bg-[#E5D3B3]" />
                      <div className="w-4 h-4 rounded-full bg-[#1A1A1A]" />
                      <div className="w-4 h-4 rounded-full bg-[#8B0000]" />
                    </div>
                  </motion.div>
                </div>

                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 1 }}
                  className="glass-card rounded-2xl p-4 w-full"
                >
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm font-medium text-white">Outfit Recommendation</span>
                    <span className="text-xs text-blue-400">Match Found</span>
                  </div>
                  <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-white rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: "85%" }}
                      transition={{ delay: 1.5, duration: 1 }}
                    />
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
