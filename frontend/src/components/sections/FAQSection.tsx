import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Plus } from "lucide-react"

const faqs = [
  {
    question: "How accurate is the Virtual Try-On?",
    answer: "Our AI model uses advanced depth mapping and cloth physics simulation to achieve a 95% photorealistic accuracy, taking into account your body type, posture, and lighting conditions."
  },
  {
    question: "Do I need a special camera to scan my body?",
    answer: "No, a standard smartphone camera in a well-lit room is all you need. Our neural network infers 3D structure from 2D images."
  },
  {
    question: "Which brands are supported in the app?",
    answer: "We partner with over 500+ luxury and premium streetwear brands including Dior, Gucci, Balenciaga, Acne Studios, and many more. The catalog updates weekly."
  },
  {
    question: "Is my personal data and photos secure?",
    answer: "Yes. All images are processed with end-to-end encryption and we do not store your photos on our servers without explicit permission. Your data is yours."
  }
]

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-6 max-w-3xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Common <span className="text-gradient">Questions</span>
          </h2>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass-card rounded-2xl overflow-hidden"
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  className="w-full flex items-center justify-between p-6 text-left focus:outline-none"
                >
                  <span className="text-lg font-medium text-white">{faq.question}</span>
                  <motion.div
                    animate={{ rotate: isOpen ? 45 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center shrink-0 ml-4"
                  >
                    <Plus className="w-4 h-4 text-white" />
                  </motion.div>
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                    >
                      <div className="p-6 pt-0 text-white/60 leading-relaxed">
                        {faq.answer}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
