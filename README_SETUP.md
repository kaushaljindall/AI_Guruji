# AI Guruji System Setup

## System Architecture
- **Backend**: FastAPI (Python)
  - Port: `8000`
  - Location: `/backend`
  - Key Services: RAG (FAISS + SentenceTransformers), Upload, Generate, Orchestrator.
- **Frontend**: React + Vite + Tailwind CSS
  - Port: `5173`
  - Location: `/frontend`
  - Design: Premium Glassmorphism.

## 📋 Prerequisites
Ensure you have the following installed before starting:
1.  **Python 3.10+**
2.  **Node.js 18+**
3.  **FFmpeg**: Required for audio processing (`pydub`).
    - **Windows (Recommended)**: Run `winget install Gyan.FFmpeg` in PowerShell.
    - **Manual**: [Download FFmpeg](https://ffmpeg.org/download.html) and add the `bin` folder to your System PATH.
    - *Verify installation by running `ffmpeg -version` in a terminal.*
4.  **(Optional) Ollama**: For local LLM inference if you don't use Gemini.

## 🚀 How to Run

### 0. Configuration
1.  **Environment Variables**:
    - Duplicate `.env.example` to `.env` in the `backend/` directory.
    - Open `backend/.env` and add your `GEMINI_API_KEY`.
    - *Note: If `GEMINI_API_KEY` is left empty, the system will automatically fallback to **Ollama** (Local LLM).*

### 1. Start Backend
The backend handles all logic, including PDF parsing, RAG, and image/audio generation.

```bash
cd backend

# 1. Install Python Dependencies
pip install -r requirements.txt

# 2. Install Playwright Browsers (Required for slide generation)
playwright install

# 3. Start the Server
uvicorn app.main:app --reload
```
*API Docs will be available at http://localhost:8000/docs*

### 2. Start Frontend
The frontend provides a modern, responsive UI for interacting with the guru.

```bash
cd frontend

# 1. Install Node Dependencies
npm install

# 2. Start Dev Server
npm run dev
```
*App will be available at http://localhost:5173*

## 🧠 Local LLM Setup (Ollama)
If you prefer running locally (free, private) instead of using Google Gemini:
1.  **Install Ollama** from [ollama.com](https://ollama.com).
2.  **Pull Helper Model**: Run `ollama pull mistral`.
3.  **Ensure Server is Running**: Check http://localhost:11434.
4.  **Configure `.env`**: Leave `GEMINI_API_KEY` blank.

## 📁 File Structure
- `backend/app/main.py`: Entry point for FastAPI.
- `backend/app/services/`: Business logic (Orchestrator, RAG, Generators).
- `frontend/src/App.jsx`: Main application wrapper.
- `frontend/src/components/`: Reusable UI components.
