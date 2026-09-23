import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Link } from "react-router-dom"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"
import { Button } from "../../components/ui/button"

export function VerifyEmailPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")

  useEffect(() => {
    // Simulate verification process
    const timer = setTimeout(() => {
      setStatus("success") // change to error to see error state
    }, 2500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center text-center gap-6 py-8"
    >
      <AnimatePresence mode="wait">
        {status === "loading" && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="relative w-20 h-20 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-2 border-white/10" />
              <div className="absolute inset-0 rounded-full border-t-2 border-purple-500 animate-spin" />
              <Loader2 className="w-8 h-8 text-white/50" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white mb-2">Verifying email</h1>
              <p className="text-white/50 text-sm">Please wait while we verify your email address.</p>
            </div>
          </motion.div>
        )}

        {status === "success" && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-4 w-full"
          >
            <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mb-2">
              <CheckCircle2 className="w-10 h-10 text-green-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white mb-2">Email verified</h1>
              <p className="text-white/50 text-sm mb-6">Your email has been successfully verified.</p>
            </div>
            <Button asChild className="w-full">
              <Link to="/login">Continue to Login</Link>
            </Button>
          </motion.div>
        )}

        {status === "error" && (
          <motion.div
            key="error"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-4 w-full"
          >
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mb-2">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white mb-2">Verification failed</h1>
              <p className="text-white/50 text-sm mb-6">The verification link is invalid or has expired.</p>
            </div>
            <Button asChild className="w-full">
              <Link to="/login">Back to Login</Link>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
