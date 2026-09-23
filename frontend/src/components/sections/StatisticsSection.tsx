import { useInView } from "framer-motion"
import { useRef, useEffect, useState } from "react"

function Counter({ end, suffix, label }: { end: number, suffix: string, label: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-50px" })
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (isInView) {
      let start = 0
      const duration = 2000 // 2 seconds
      const increment = end / (duration / 16) // 60fps

      const timer = setInterval(() => {
        start += increment
        if (start > end) {
          setCount(end)
          clearInterval(timer)
        } else {
          setCount(Math.floor(start))
        }
      }, 16)
      return () => clearInterval(timer)
    }
  }, [isInView, end])

  return (
    <div ref={ref} className="flex flex-col items-center justify-center p-8 text-center">
      <h4 className="text-5xl md:text-7xl font-bold text-white mb-4 tracking-tighter">
        {count}{suffix}
      </h4>
      <p className="text-white/60 text-lg uppercase tracking-widest font-medium">
        {label}
      </p>
    </div>
  )
}

export function StatisticsSection() {
  return (
    <section className="py-24 border-y border-white/5 bg-gradient-to-b from-white/[0.02] to-transparent">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 divide-y md:divide-y-0 md:divide-x divide-white/10">
          <Counter end={95} suffix="%" label="Recommendation Accuracy" />
          <Counter end={100} suffix="K+" label="Generated Outfits" />
          <Counter end={500} suffix="+" label="Fashion Styles" />
        </div>
      </div>
    </section>
  )
}
