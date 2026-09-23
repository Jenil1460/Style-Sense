import * as React from "react"
import { motion } from "framer-motion"
import { Button } from "./button"

interface SocialButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode
  provider: string
}

export function SocialButton({ icon, provider, ...props }: SocialButtonProps) {
  return (
    <motion.div whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} className="w-full">
      <Button
        variant="outline"
        className="w-full h-12 rounded-2xl border-white/10 bg-white/[0.03] hover:bg-white/[0.08] text-white flex items-center justify-center gap-3 transition-colors"
        {...props}
      >
        {icon}
        <span className="font-medium">Continue with {provider}</span>
      </Button>
    </motion.div>
  )
}
