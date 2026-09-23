import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Link } from "react-router-dom"
import { Lock, Loader2, CheckCircle2 } from "lucide-react"
import { Input } from "../../components/ui/input"
import { Button } from "../../components/ui/button"
import { PasswordStrength } from "../../components/ui/PasswordStrength"

export function ResetPasswordPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      setIsSuccess(true)
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
      <div className="mb-2">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Set new password</h1>
        <p className="text-white/50 text-sm">Please choose a strong password.</p>
      </div>

      <AnimatePresence mode="wait">
        {!isSuccess ? (
          <motion.form
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onSubmit={handleSubmit}
            className="flex flex-col gap-4"
          >
            <div className="flex flex-col">
              <Input
                type="password"
                placeholder="New password"
                icon={<Lock className="w-4 h-4" />}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <PasswordStrength password={password} />
            </div>

            <Input
              type="password"
              placeholder="Confirm new password"
              icon={<Lock className="w-4 h-4" />}
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              error={confirmPassword && password !== confirmPassword ? "Passwords do not match" : undefined}
            />

            <Button type="submit" disabled={isLoading || (password !== confirmPassword)} className="w-full mt-2 group relative overflow-hidden">
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="relative z-10">Reset Password</span>
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
            <h3 className="text-xl font-medium text-white">Password reset complete</h3>
            <p className="text-sm text-white/60 mb-4">
              Your password has been successfully updated.
            </p>
            <Button asChild className="w-full">
              <Link to="/login">Go to Login</Link>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
