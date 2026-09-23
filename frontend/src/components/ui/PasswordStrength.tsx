import { motion } from "framer-motion"

interface PasswordStrengthProps {
  password?: string
}

export function PasswordStrength({ password = "" }: PasswordStrengthProps) {
  const calculateStrength = (pass: string) => {
    let score = 0
    if (!pass) return 0
    if (pass.length > 8) score += 1
    if (pass.match(/[a-z]/) && pass.match(/[A-Z]/)) score += 1
    if (pass.match(/\d/)) score += 1
    if (pass.match(/[^a-zA-Z\d]/)) score += 1
    return score
  }

  const score = calculateStrength(password)

  const bars = Array.from({ length: 4 }).map((_, i) => {
    const isActive = i < score
    let color = "bg-white/10"
    let glow = ""
    
    if (isActive) {
      if (score === 1) {
        color = "bg-red-500"
        glow = "shadow-[0_0_10px_rgba(239,68,68,0.5)]"
      } else if (score === 2) {
        color = "bg-orange-500"
        glow = "shadow-[0_0_10px_rgba(249,115,22,0.5)]"
      } else if (score === 3) {
        color = "bg-yellow-500"
        glow = "shadow-[0_0_10px_rgba(234,179,8,0.5)]"
      } else {
        color = "bg-green-500"
        glow = "shadow-[0_0_10px_rgba(34,197,94,0.5)]"
      }
    }

    return (
      <motion.div
        key={i}
        className={`h-1.5 w-full rounded-full transition-colors duration-500 ${color} ${glow}`}
        initial={{ opacity: 0.5 }}
        animate={{ opacity: isActive ? 1 : 0.3 }}
      />
    )
  })

  let text = "Password strength"
  let textColor = "text-white/40"
  if (score === 1) { text = "Weak"; textColor = "text-red-400" }
  if (score === 2) { text = "Fair"; textColor = "text-orange-400" }
  if (score === 3) { text = "Good"; textColor = "text-yellow-400" }
  if (score === 4) { text = "Strong"; textColor = "text-green-400" }

  return (
    <div className="flex flex-col gap-2 w-full mt-2">
      <div className="flex gap-1.5 w-full">{bars}</div>
      {password && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`text-xs ${textColor} font-medium`}
        >
          {text}
        </motion.span>
      )}
    </div>
  )
}
