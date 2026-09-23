import { useState } from "react"
import { motion } from "framer-motion"
import { Link, useNavigate } from "react-router-dom"
import { Mail, Lock, User, Loader2 } from "lucide-react"
import { Input } from "../../components/ui/input"
import { Button } from "../../components/ui/button"
import { PasswordStrength } from "../../components/ui/PasswordStrength"
import { api } from "../../lib/api"
import { extractErrorMessage } from "../../lib/utils"
import toast from "react-hot-toast"

export function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await api.post('/auth/register', {
        email,
        password,
        first_name: firstName,
        last_name: lastName
      });
      toast.success("Account created! Please log in.");
      navigate('/login');
    } catch (error: any) {
      toast.error(extractErrorMessage(error, "Registration failed."));
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
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Create an account</h1>
        <p className="text-white/50 text-sm">Join StyleSense AI today.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            placeholder="First name"
            icon={<User className="w-4 h-4" />}
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <Input
            placeholder="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>

        <Input
          type="email"
          placeholder="Email address"
          icon={<Mail className="w-4 h-4" />}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <div className="flex flex-col">
          <Input
            type="password"
            placeholder="Password"
            icon={<Lock className="w-4 h-4" />}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <PasswordStrength password={password} />
        </div>

        <Button type="submit" disabled={isLoading} className="w-full mt-4 group relative overflow-hidden">
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <span className="relative z-10">Create Account</span>
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
            </>
          )}
        </Button>
      </form>

      <p className="text-xs text-white/40 text-center mt-2 leading-relaxed">
        By clicking continue, you agree to our{" "}
        <a href="#" className="underline hover:text-white transition-colors">Terms of Service</a>{" "}
        and{" "}
        <a href="#" className="underline hover:text-white transition-colors">Privacy Policy</a>.
      </p>

      <div className="text-center mt-2">
        <p className="text-sm text-white/50">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-white hover:underline underline-offset-4">
            Sign in
          </Link>
        </p>
      </div>
    </motion.div>
  )
}
