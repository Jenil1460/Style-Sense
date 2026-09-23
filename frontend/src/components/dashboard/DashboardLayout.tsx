import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopNav } from "./TopNav"

export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-[#050505] text-white flex selection:bg-purple-500/30 selection:text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopNav />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 pb-24">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
