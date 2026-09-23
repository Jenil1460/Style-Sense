# StyleSense AI Backend

This is the production-ready FastAPI backend for StyleSense AI.

## Architecture

- **Framework**: FastAPI (Async)
- **Database**: MongoDB Atlas with Motor (Async MongoDB driver)
- **Authentication**: JWT & Bcrypt
- **File Storage**: Cloudinary integration
- **Validation**: Pydantic v2

## Setup Instructions

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your credentials.

4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **API Documentation**:
   Once the server is running, visit:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
