import { motion } from "framer-motion"
import { Link, useLocation } from "react-router-dom"
import { Sparkles, LayoutDashboard, Shirt, History, BarChart2, Settings, LogOut } from "lucide-react"
import { useAuth } from "../../context/AuthContext"

const navItems = [
  { icon: LayoutDashboard, label: "Overview", path: "/dashboard" },
  { icon: Shirt, label: "Wardrobe", path: "/dashboard/wardrobe" },
  { icon: History, label: "History", path: "/dashboard/history" },
  { icon: BarChart2, label: "Statistics", path: "/dashboard/statistics" },
]

export function Sidebar() {
  const location = useLocation()
  const { logout } = useAuth()

  return (
    <div className="w-64 h-screen hidden lg:flex flex-col border-r border-white/5 bg-[#0a0a0a]/80 backdrop-blur-3xl sticky top-0">

      {/* Brand */}
      <div className="p-6 flex items-center gap-2">
        <Sparkles className="w-6 h-6 text-white" />
        <span className="text-xl font-bold tracking-tight text-white">StyleSense</span>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-4 py-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon

          return (
            <Link key={item.path} to={item.path} className="block relative">
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 bg-white/10 rounded-xl"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <div className={`relative flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${isActive ? 'text-white' : 'text-white/50 hover:text-white/80 hover:bg-white/5'}`}>
                <Icon className="w-5 h-5" />
                <span className="font-medium text-sm">{item.label}</span>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Footer Nav */}
      <div className="p-4 space-y-2 border-t border-white/5">
        <Link to="/dashboard/settings" className="flex items-center gap-3 px-4 py-3 rounded-xl text-white/50 hover:text-white hover:bg-white/5 transition-colors">
          <Settings className="w-5 h-5" />
          <span className="font-medium text-sm">Settings</span>
        </Link>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400/70 hover:text-red-400 hover:bg-red-400/10 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium text-sm">Log out</span>
        </button>
      </div>

    </div>
  )
}
