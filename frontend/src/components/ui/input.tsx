import * as React from "react"
import { motion } from "framer-motion"
import { cn } from "../../lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
  icon?: React.ReactNode
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, icon, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute left-4 text-white/50 pointer-events-none">
              {icon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              "flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white placeholder:text-white/30 transition-all duration-300",
              "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white/30 focus-visible:border-white/30 focus-visible:bg-white/10",
              "disabled:cursor-not-allowed disabled:opacity-50",
              icon && "pl-11",
              error && "border-red-500/50 focus-visible:ring-red-500/30 focus-visible:border-red-500/50",
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-red-400 text-xs mt-2 ml-1"
          >
            {error}
          </motion.p>
        )}
      </div>
    )
  }
)
Input.displayName = "Input"

export { Input }
