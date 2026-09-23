import { useState } from "react"
import { motion } from "framer-motion"
import { Link, useNavigate } from "react-router-dom"
import { Mail, Lock, Loader2 } from "lucide-react"
import { Input } from "../../components/ui/input"
import { Button } from "../../components/ui/button"
import { SocialButton } from "../../components/ui/SocialButton"
import { useAuth } from "../../context/AuthContext"
import { api } from "../../lib/api"
import { extractErrorMessage } from "../../lib/utils"
import toast from "react-hot-toast"

// Simple SVG Icons for Socials
const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5">
    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
  </svg>
)
const AppleIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5">
    <path fill="currentColor" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.05 2.25.68 2.74.68.42 0 1.64-.81 3.31-.76 1.76.05 3.03.74 3.79 1.83-3.26 1.76-2.72 6.09.46 7.42-.72 1.69-1.63 3.12-2.3 3.79zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
  </svg>
)

export function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const response = await api.post('/auth/login', {
        email: email,
        password: password
      });

      login(response.data.access_token, response.data.user);
      toast.success("Successfully logged in!");
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(extractErrorMessage(error, "Failed to login. Check credentials."));
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col gap-6"
    >
      <div className="text-center mb-2">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Welcome back</h1>
        <p className="text-white/50 text-sm">Log in to your StyleSense AI account.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          type="email"
          placeholder="Email address"
          icon={<Mail className="w-4 h-4" />}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Input
          type="password"
          placeholder="Password"
          icon={<Lock className="w-4 h-4" />}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <div className="flex justify-end mt-1">
          <Link to="/forgot-password" className="text-sm font-medium text-white/60 hover:text-white transition-colors">
            Forgot password?
          </Link>
        </div>

        <Button type="submit" disabled={isLoading} className="w-full mt-2 group relative overflow-hidden">
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <span className="relative z-10">Sign in</span>
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
            </>
          )}
        </Button>
      </form>

      <div className="relative my-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/10"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-[#0c0c0c] px-2 text-white/40 rounded-full">Or continue with</span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <SocialButton icon={<GoogleIcon />} provider="Google" />
        <SocialButton icon={<AppleIcon />} provider="Apple" />
      </div>

      <div className="text-center mt-4">
        <p className="text-sm text-white/50">
          Don't have an account?{" "}
          <Link to="/register" className="font-medium text-white hover:underline underline-offset-4">
            Sign up
          </Link>
        </p>
      </div>
    </motion.div>
  )
}
