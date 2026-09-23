import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Navbar } from "./components/layout/Navbar"
import { HeroSection } from "./components/sections/HeroSection"
import { FeaturesSection } from "./components/sections/FeaturesSection"
import { HowItWorksSection } from "./components/sections/HowItWorksSection"
import { ShowcaseSection } from "./components/sections/ShowcaseSection"
import { StatisticsSection } from "./components/sections/StatisticsSection"
import { TestimonialsSection } from "./components/sections/TestimonialsSection"
import { FAQSection } from "./components/sections/FAQSection"
import { FooterSection } from "./components/sections/FooterSection"

import { AuthLayout } from "./components/layout/AuthLayout"
import { LoginPage } from "./pages/auth/LoginPage"
import { RegisterPage } from "./pages/auth/RegisterPage"
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage"
import { ResetPasswordPage } from "./pages/auth/ResetPasswordPage"
import { VerifyEmailPage } from "./pages/auth/VerifyEmailPage"

import { DashboardLayout } from "./components/dashboard/DashboardLayout"
import { DashboardPage } from "./pages/dashboard/DashboardPage"
import { SettingsPage } from "./pages/dashboard/SettingsPage"
import { HistoryPage } from "./pages/dashboard/HistoryPage"
import { WardrobePage } from "./pages/dashboard/WardrobePage"
import { StatisticsPage } from "./pages/dashboard/StatisticsPage"
import { ResultsPage } from "./pages/dashboard/ResultsPage"

function LandingPage() {
  return (
    <div className="min-h-screen bg-[#050505] text-white selection:bg-purple-500/30 selection:text-white">
      <Navbar />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <ShowcaseSection />
        <StatisticsSection />
        <TestimonialsSection />
        <FAQSection />
      </main>
      <FooterSection />
    </div>
  )
}

import { AuthProvider } from "./context/AuthContext"
import { Toaster } from "react-hot-toast"
import { ProtectedRoute } from "./components/layout/ProtectedRoute"
import { ErrorBoundary } from "./components/layout/ErrorBoundary"

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Toaster position="top-center" toastOptions={{
            style: {
              background: '#111',
              color: '#fff',
              border: '1px solid rgba(255,255,255,0.1)',
            }
          }} />
          <Routes>
          <Route path="/" element={<LandingPage />} />
          
          {/* Auth Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
          </Route>

          {/* Dashboard Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="wardrobe" element={<WardrobePage />} />
              <Route path="statistics" element={<StatisticsPage />} />
              <Route path="results/:id" element={<ResultsPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
