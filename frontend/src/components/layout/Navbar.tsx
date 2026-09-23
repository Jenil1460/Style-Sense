import { useState } from "react"
import { motion, useScroll, useMotionValueEvent } from "framer-motion"
import { Sparkles, Menu, X } from "lucide-react"
import { cn } from "../../lib/utils"
import { Link } from "react-router-dom"
import { buttonVariants } from "../ui/button"

export function Navbar() {
  const { scrollY } = useScroll()
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50)
  })

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? "py-4" : "py-6"
        }`}
    >
      <div className="container mx-auto px-6">
        <div className={`flex items-center justify-between rounded-full px-6 py-3 transition-all duration-300 ${isScrolled ? "glass-card" : "bg-transparent"
          }`}>
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-white" />
            <span className="text-xl font-bold tracking-tight text-white">StyleSense</span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8">
            <a href="#" className="text-sm font-medium text-white/70 hover:text-white transition-colors">Features</a>
            <a href="#" className="text-sm font-medium text-white/70 hover:text-white transition-colors">How it Works</a>
            <a href="#" className="text-sm font-medium text-white/70 hover:text-white transition-colors">Testimonials</a>
            <a href="#" className="text-sm font-medium text-white/70 hover:text-white transition-colors">FAQ</a>
          </nav>

          {/* Actions */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/login" className={cn(buttonVariants({ variant: "ghost" }), "hidden lg:flex")}>Log in</Link>
            <Link to="/register" className={buttonVariants({ size: "sm" })}>Get Started</Link>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden text-white p-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute top-full left-0 right-0 p-4 mt-2"
        >
          <div className="glass-card rounded-2xl p-6 flex flex-col gap-4">
            <a href="#" className="text-white font-medium p-2">Features</a>
            <a href="#" className="text-white font-medium p-2">How it Works</a>
            <a href="#" className="text-white font-medium p-2">Testimonials</a>
            <a href="#" className="text-white font-medium p-2">FAQ</a>
            <hr className="border-white/10 my-2" />
            <Link to="/login" className={cn(buttonVariants({ variant: "ghost" }), "w-full justify-start")}>Log in</Link>
            <Link to="/register" className={cn(buttonVariants(), "w-full")}>Get Started</Link>
          </div>
        </motion.div>
      )}
    </motion.header>
  )
}
