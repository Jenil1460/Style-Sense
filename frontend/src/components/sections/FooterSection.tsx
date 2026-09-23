import { Sparkles } from "lucide-react"

export function FooterSection() {
  return (
    <footer className="pt-24 pb-8 border-t border-white/5 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[1000px] h-[300px] bg-blue-500/5 rounded-t-full blur-[100px] pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-6 h-6 text-white" />
              <span className="text-xl font-bold text-white tracking-tight">StyleSense AI</span>
            </div>
            <p className="text-white/50 text-sm leading-relaxed mb-6">
              Your Personal AI Fashion Stylist. Revolutionizing how you discover, try, and wear fashion through artificial intelligence.
            </p>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-white/10 hover:text-white transition-colors">
                X
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-white/10 hover:text-white transition-colors">
                IG
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/70 hover:bg-white/10 hover:text-white transition-colors">
                IN
              </a>
            </div>
          </div>

          <div>
            <h4 className="text-white font-medium mb-6">Product</h4>
            <ul className="space-y-4">
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Features</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Virtual Try-On</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Pricing</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Changelog</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-medium mb-6">Company</h4>
            <ul className="space-y-4">
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">About Us</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Careers</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Blog</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Contact</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-medium mb-6">Legal</h4>
            <ul className="space-y-4">
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Privacy Policy</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Terms of Service</a></li>
              <li><a href="#" className="text-white/50 hover:text-white transition-colors text-sm">Cookie Policy</a></li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/5">
          <p className="text-white/30 text-xs mb-4 md:mb-0">
            © {new Date().getFullYear()} StyleSense AI. All rights reserved.
          </p>
          <div className="flex items-center gap-2 text-white/30 text-xs">
            <span>Designed in California</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
