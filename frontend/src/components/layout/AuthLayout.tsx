import { motion } from "framer-motion"
import { Sparkles } from "lucide-react"
import { Outlet, Link } from "react-router-dom"

export function AuthLayout() {
  return (
    <div className="min-h-screen flex bg-background selection:bg-purple-500/30 selection:text-white relative overflow-hidden">

      {/* Left Side - Ambient Environment (Hidden on mobile) */}
      <div className="hidden lg:flex w-1/2 relative bg-black items-center justify-center overflow-hidden">

        {/* Background Mesh Gradients */}
        <div className="absolute inset-0 pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[100px]"
          />
          <motion.div
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{ duration: 15, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[120px]"
          />
        </div>

        {/* Particles */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none mix-blend-overlay" />

        {/* Floating Cards & Illustration */}
        <div className="relative z-10 w-full max-w-lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="glass-card rounded-[2rem] p-8 aspect-[4/5] relative overflow-hidden border-white/5 bg-white/[0.02]"
          >
            <div className="absolute inset-0">
              <img
                src="https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=1000&auto=format&fit=crop"
                alt="Fashion Model"
                className="w-full h-full object-cover opacity-60"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
            </div>

            <div className="relative z-10 h-full flex flex-col justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-white" />
                <span className="text-xl font-bold tracking-tight text-white">StyleSense</span>
              </div>

              <div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                >
                  <h2 className="text-3xl font-bold text-white mb-2">Elevate your style.</h2>
                  <p className="text-white/60">Join the next generation of fashion discovery.</p>
                </motion.div>
              </div>
            </div>

            {/* Floating Element 1 */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="absolute top-1/4 -right-12 glass-card p-4 rounded-2xl flex items-center gap-3 backdrop-blur-md"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-sm font-medium text-white">Match Found</div>
                <div className="text-xs text-white/50">98% Compatibility</div>
              </div>
            </motion.div>

          </motion.div>
        </div>
      </div>

      {/* Right Side - Auth Forms */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 relative">
        <div className="absolute inset-0 pointer-events-none lg:hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px]" />
        </div>

        <Link to="/" className="absolute top-6 left-6 lg:hidden flex items-center gap-2 z-50">
          <Sparkles className="w-5 h-5 text-white" />
          <span className="text-xl font-bold tracking-tight text-white">StyleSense</span>
        </Link>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md relative z-10"
        >
          <div className="glass-card rounded-[2rem] p-8 md:p-10 border-white/5 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
            <Outlet />
          </div>
        </motion.div>
      </div>

    </div>
  )
}
