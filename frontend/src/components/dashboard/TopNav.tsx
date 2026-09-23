import { Search, Bell, Sparkles, Menu } from "lucide-react"
import { motion } from "framer-motion"
import { useAuth } from "../../context/AuthContext"

export function TopNav() {
  const { user } = useAuth()

  return (
    <header className="h-20 border-b border-white/5 bg-[#050505]/80 backdrop-blur-3xl sticky top-0 z-40 px-6 flex items-center justify-between">

      {/* Mobile Menu & Search */}
      <div className="flex items-center gap-4 flex-1">
        <button className="lg:hidden text-white/70 hover:text-white">
          <Menu className="w-6 h-6" />
        </button>
        <div className="relative w-full max-w-md hidden md:flex items-center">
          <Search className="w-4 h-4 text-white/40 absolute left-4" />
          <input
            type="text"
            placeholder="Search outfits, styles, history..."
            className="w-full bg-white/5 border border-white/10 rounded-full h-10 pl-11 pr-4 text-sm text-white placeholder:text-white/40 focus:outline-none focus:bg-white/10 focus:border-white/20 transition-all"
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        {/* AI Assistant Trigger */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="hidden md:flex items-center gap-2 bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30 hover:border-purple-500/50 px-4 py-2 rounded-full transition-all"
        >
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-sm font-medium text-white/90">AI Assistant</span>
        </motion.button>

        {/* Notifications */}
        <button className="relative w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/70 hover:bg-white/10 hover:text-white transition-all">
          <Bell className="w-4 h-4" />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-purple-500 rounded-full border-2 border-[#050505]" />
        </button>

        {/* Profile Avatar */}
        <button className="w-10 h-10 rounded-full overflow-hidden border border-white/20 hover:border-white/40 transition-colors bg-white/5 flex items-center justify-center">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt="Profile"
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-white font-medium text-sm">{user?.first_name?.charAt(0) || 'U'}</span>
          )}
        </button>
      </div>

    </header>
  )
}
