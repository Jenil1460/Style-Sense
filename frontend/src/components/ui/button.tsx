import * as React from "react"

import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white/20 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-white text-black hover:bg-white/90 shadow-[0_0_20px_rgba(255,255,255,0.3)]",
        destructive:
          "bg-red-500 text-neutral-50 hover:bg-red-500/90",
        outline:
          "border border-white/20 bg-transparent hover:bg-white/10 text-white",
        secondary:
          "bg-white/10 text-white hover:bg-white/20",
        ghost: "hover:bg-white/10 hover:text-white text-white/70",
        link: "text-white underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-6 py-2",
        sm: "h-8 rounded-full px-4 text-xs",
        lg: "h-12 rounded-full px-8 text-base",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    // using a simple component fallback since we didn't install radix-ui/react-slot
    const Comp = asChild ? "span" : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref as any}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
