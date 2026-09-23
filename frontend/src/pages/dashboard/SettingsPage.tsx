import { useState, useEffect, useRef } from "react";
import { User, Upload, Loader2, Save } from "lucide-react";
import { api } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import { extractErrorMessage } from "../../lib/utils";
import toast from "react-hot-toast";

export function SettingsPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);


  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    gender: "",
    height: "",
    weight: "",
    body_type: "",
    preferred_styles: "",
    favorite_colors: "",
  });

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        gender: user.gender || "",
        height: user.height ? user.height.toString() : "",
        weight: user.weight ? user.weight.toString() : "",
        body_type: user.body_type || "",
        preferred_styles: user.preferred_styles?.join(", ") || "",
        favorite_colors: user.favorite_colors?.join(", ") || "",
      });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const payload = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        gender: formData.gender || undefined,
        body_type: formData.body_type || undefined,
        height: formData.height ? parseFloat(formData.height) : undefined,
        weight: formData.weight ? parseFloat(formData.weight) : undefined,
        preferred_styles: formData.preferred_styles ? formData.preferred_styles.split(",").map(s => s.trim()).filter(s => s) : [],
        favorite_colors: formData.favorite_colors ? formData.favorite_colors.split(",").map(s => s.trim()).filter(s => s) : [],
      };

      await api.put('/profile/', payload);
      toast.success("Profile updated successfully! Refresh to see changes globally.");
    } catch (error) {
      console.error(error);
      toast.error("Failed to update profile.");
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];

    setAvatarUploading(true);
    try {
      const uploadData = new FormData();
      uploadData.append('file', file);

      await api.post('/profile/avatar', uploadData);

      toast.success("Avatar updated successfully! Please refresh to see changes.");
    } catch (error: any) {
      console.error("Upload error details:", error.response?.data || error);
      toast.error(extractErrorMessage(error, "Failed to upload avatar."));
    } finally {
      setAvatarUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-white/50">Manage your profile and styling preferences.</p>
      </div>

      <div className="glass-card rounded-3xl p-8 border-white/5 space-y-8">

        {/* Avatar Section */}
        <div className="flex items-center gap-6 pb-8 border-b border-white/10">
          <div className="w-24 h-24 rounded-full overflow-hidden bg-white/5 flex items-center justify-center border border-white/20">
            {avatarUploading ? (
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
            ) : user?.avatar_url ? (
              <img src={user.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
            ) : (
              <User className="w-10 h-10 text-white/50" />
            )}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Profile Picture</h3>
            <div className="flex items-center gap-4">
              <input type="file" ref={fileInputRef} onChange={handleAvatarUpload} className="hidden" accept="image/*" />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={avatarUploading}
                className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-xl transition-colors font-medium text-sm disabled:opacity-50"
              >
                <Upload className="w-4 h-4" />
                Upload New
              </button>
            </div>
          </div>
        </div>

        {/* Profile Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">First Name</label>
            <input
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="First Name"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">Last Name</label>
            <input
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="Last Name"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-purple-500/50 transition-colors"
            >
              <option value="">Select...</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Non-binary">Non-binary</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">Body Type</label>
            <select
              name="body_type"
              value={formData.body_type}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-purple-500/50 transition-colors"
            >
              <option value="">Select...</option>
              <option value="Slim">Slim</option>
              <option value="Athletic">Athletic</option>
              <option value="Average">Average</option>
              <option value="Plus-size">Plus-size</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">Height (cm)</label>
            <input
              name="height"
              type="number"
              value={formData.height}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="e.g. 175"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-white/70">Weight (kg)</label>
            <input
              name="weight"
              type="number"
              value={formData.weight}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="e.g. 70"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-medium text-white/70">Preferred Styles (comma separated)</label>
            <input
              name="preferred_styles"
              value={formData.preferred_styles}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="e.g. Minimalist, Streetwear, Business Casual"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-medium text-white/70">Favorite Colors (comma separated)</label>
            <input
              name="favorite_colors"
              value={formData.favorite_colors}
              onChange={handleChange}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-purple-500/50 transition-colors"
              placeholder="e.g. Black, White, Navy Blue"
            />
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t border-white/10">
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex items-center gap-2 bg-purple-500 hover:bg-purple-600 text-white px-8 py-3 rounded-xl transition-colors font-medium text-sm shadow-[0_0_20px_rgba(168,85,247,0.4)] disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Changes
          </button>
        </div>

      </div>
    </div>
  );
}
