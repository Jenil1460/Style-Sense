# StyleSense AI 👗✨

**StyleSense AI** is a real-time, zero-hallucination AI fashion stylist and outfit analysis web application. It combines deep learning computer vision (YOLOv8, MediaPipe, CLIP ViT-B-32) with FastAPI and React to deliver personalized style recommendations, personal color analysis, body type estimation, and virtual try-on in under 4 seconds.

---

## 🌟 Key Features

- **Multi-Strategy Person & Pose Detection**: YOLOv8 + MediaPipe skeleton landmark extraction.
- **Landmark-Guided Garment Segmentation & Color Extraction**: GrabCut with HSV/YCrCb masking and K-Means color clustering.
- **Zero-Shot Style & Occasion Classification**: Fast CLIP ViT-B-32 with precomputed text embeddings.
- **ITA-Based Skin Tone & Undertone Analysis**: Gray-World white-balanced individual typology angle classification.
- **Geometric Face Shape & Body Type Estimation**: Landmark shoulder-to-hip proportions and facial landmark geometry.
- **AI Fashion Narrative & Recommendations**: Radar metric scoring, seasonal styling advice, and Gemini AI fashion summaries.
- **Virtual Try-On (VTON)**: Realistic garment transfer preview powered by generative models.

---

## 🏗️ Architecture

```
StyleSense-AI/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── ai/               # Computer vision & ML detectors (YOLO, CLIP, MediaPipe)
│   │   ├── api/              # FastAPI REST endpoints
│   │   ├── services/         # Orchestrator, upload, try-on & ML services
│   │   ├── database/         # MongoDB connection & collections
│   │   └── models/           # Pydantic schemas & DB models
│   └── requirements.txt
├── frontend/                 # React + TypeScript + Tailwind CSS + Vite
│   ├── src/
│   │   ├── components/       # UI & dashboard components
│   │   ├── pages/            # App routes & views
│   │   └── lib/              # API clients & utilities
│   └── package.json
└── README.md
```

---

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Environment Configuration

Create a `.env` file in `backend/` with:
```env
MONGODB_URI=mongodb+srv://...
JWT_SECRET=your_secret_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
GEMINI_API_KEY=your_gemini_api_key
```

---

## 📄 License
MIT License
