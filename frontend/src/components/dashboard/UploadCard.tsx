import { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, X, Image as ImageIcon, Loader2 } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { api } from "../../lib/api"
import { extractErrorMessage } from "../../lib/utils"
import toast from "react-hot-toast"

interface UploadCardProps {
  onUploadComplete?: () => void;
}

export function UploadCard({ onUploadComplete }: UploadCardProps) {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [statusText, setStatusText] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true)
    else if (e.type === "dragleave") setDragActive(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (selectedFile: File) => {
    // Client-side type check
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error("Unsupported file type. Please upload a JPEG, PNG, or WEBP image.");
      return;
    }
    // Client-side size check (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      toast.error("File is too large. Maximum size is 10MB.");
      return;
    }
    setFile(selectedFile);
    const url = URL.createObjectURL(selectedFile);
    setPreview(url);
  }

  const startUpload = async () => {
    if (!file) return
    setIsUploading(true)
    try {
      setStatusText("Validating image...")
      const formData = new FormData();
      formData.append('file', file);

      setStatusText("Uploading outfit...")
      const uploadRes = await api.post('/uploads/image', formData);

      const uploadId = uploadRes.data.id;

      setStatusText("Analyzing outfit with StyleSense AI...")
      const analyzeRes = await api.post(`/ai/analyze/${uploadId}`);

      toast.success("Outfit successfully analyzed!");

      if (onUploadComplete) onUploadComplete();

      reset();
      navigate(`/dashboard/results/${analyzeRes.data.id}`);
    } catch (error: any) {
      console.error("Upload error details:", error.response?.data || error);
      toast.error(extractErrorMessage(error, "An error occurred during upload or analysis"));
    } finally {
      setIsUploading(false)
      setStatusText("")
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setIsUploading(false)
    setStatusText("")
  }

  return (
    <div className="glass-card rounded-3xl p-1 w-full max-w-2xl mx-auto border-white/5 relative group">

      {/* Animated glowing border effect on drag */}
      <motion.div
        animate={{ opacity: dragActive ? 1 : 0 }}
        className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-blue-500/30 rounded-3xl blur-md -z-10 transition-opacity duration-300"
      />

      <div
        className={`relative flex flex-col items-center justify-center p-12 rounded-[1.4rem] border-2 border-dashed transition-colors duration-300 ${dragActive ? "border-purple-400 bg-purple-400/5" : "border-white/10 hover:border-white/20 bg-black/40"
          } min-h-[300px] overflow-hidden`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="hidden"
        />

        <AnimatePresence mode="wait">
          {!preview ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center text-center pointer-events-none"
            >
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-6 text-white/50">
                <Upload className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Upload outfit photo</h3>
              <p className="text-white/40 text-sm mb-6 max-w-sm">
                Drag and drop your full-body image here, or click to browse files. Supports JPG, PNG.
              </p>
              <button
                onClick={(e) => { e.preventDefault(); inputRef.current?.click() }}
                className="bg-white text-black px-6 py-2.5 rounded-full font-medium text-sm hover:bg-white/90 transition-colors pointer-events-auto shadow-[0_0_20px_rgba(255,255,255,0.2)]"
              >
                Select Image
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 w-full h-full"
            >
              <img src={preview} alt="Preview" className="w-full h-full object-cover opacity-60" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

              {!isUploading ? (
                <div className="absolute inset-0 p-6 flex flex-col justify-between">
                  <div className="flex justify-end">
                    <button onClick={reset} className="w-8 h-8 rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center text-white/70 hover:text-white hover:bg-white/20 transition-all border border-white/10">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="flex justify-between items-end">
                    <div className="flex items-center gap-3 glass-card px-4 py-2 rounded-xl border-white/10">
                      <ImageIcon className="w-4 h-4 text-white/70" />
                      <span className="text-sm font-medium text-white truncate max-w-[150px]">{file?.name}</span>
                    </div>
                    <button
                      onClick={startUpload}
                      className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2.5 rounded-full font-medium text-sm transition-colors shadow-[0_0_20px_rgba(168,85,247,0.4)]"
                    >
                      Analyze Style
                    </button>
                  </div>
                </div>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center flex-col z-20 bg-black/60 backdrop-blur-sm">
                  {/* Scanning Line Animation */}
                  <motion.div
                    className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent shadow-[0_0_15px_rgba(168,85,247,0.8)]"
                    animate={{ top: ["0%", "100%", "0%"] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  />
                  <Loader2 className="w-10 h-10 text-purple-400 animate-spin mb-4" />
                  <p className="text-white font-medium text-lg tracking-wide">{statusText || "AI Processing..."}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
