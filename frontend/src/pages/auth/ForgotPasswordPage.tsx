import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Link } from "react-router-dom"
import { Mail, ArrowLeft, Loader2, CheckCircle2 } from "lucide-react"
import { Input } from "../../components/ui/input"
import { Button } from "../../components/ui/button"

export function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [isSent, setIsSent] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      setIsSent(true)
    }, 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col gap-6"
    >
      <Link to="/login" className="inline-flex items-center gap-2 text-sm text-white/50 hover:text-white transition-colors w-fit">
        <ArrowLeft className="w-4 h-4" /> Back to login
      </Link>

      <div className="mb-2">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Reset password</h1>
        <p className="text-white/50 text-sm">Enter your email and we'll send you a reset link.</p>
      </div>

      <AnimatePresence mode="wait">
        {!isSent ? (
          <motion.form
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onSubmit={handleSubmit}
            className="flex flex-col gap-4"
          >
            <Input
              type="email"
              placeholder="Email address"
              icon={<Mail className="w-4 h-4" />}
              required
            />

            <Button type="submit" disabled={isLoading} className="w-full mt-2 group relative overflow-hidden">
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="relative z-10">Send Reset Link</span>
                  <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                </>
              )}
            </Button>
          </motion.form>
        ) : (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center text-center py-6 gap-4"
          >
            <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mb-2">
              <CheckCircle2 className="w-8 h-8 text-green-400" />
            </div>
            <h3 className="text-xl font-medium text-white">Check your email</h3>
            <p className="text-sm text-white/60">
              We've sent a password reset link to your email.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
