# 🎓 AI Guruji - The AI Teacher System

**AI Guruji** is an advanced AI-powered educational platform that automatically converts PDF documents into professional, long-form video lectures. It uses a "Teacher Avatar," narrated speech, and dynamically generated slides to teach complex topics just like a real professor.

![AI Guruji Banner](https://via.placeholder.com/800x200?text=AI+Guruji+Platform)

## ✨ Key Features

*   **📄 PDF to Lecture**: Upload any textbook or paper; the system understands it.
*   **🧠 RAG Pipeline**: Uses Retrieval-Augmented Generation to ensure factual accuracy based *only* on the source document.
*   **🗣️ Professional Narration**: Uses **Coqui TTS** for calm, paced, teacher-style voice synthesis.
*   **📊 Auto-Slide Generation**: Creates HTML/CSS-based slides using **Playwright** that perfectly match the script.
*   **🤖 AI Avatar (Wav2Lip)**: Syncs the audio to a video avatar for a realistic classroom experience.
*   **🎼 Orchestrated Playback**: A React-based player that syncs slides and audio automatically.

## 🛠️ Tech Stack

### Backend
*   **Framework**: FastAPI (Python)
*   **LLM**: Google Gemini Pro (via `google-generativeai`)
*   **RAG**: FAISS + SentenceTransformers
*   **Audio**: Coqui TTS
*   **Vision**: Wav2Lip (Lip Sync), Playwright (Slide Rendering)

### Frontend
*   **Framework**: React (Vite)
*   **Styling**: Tailwind CSS
*   **UI**: Glassmorphism Design, Lucide Icons

## 🚀 Getting Started

For detailed installation and run instructions, please see the **[Setup Guide](README_SETUP.md)**.

### Quick Start
1.  **Configure**: Rename `backend/.env.example` to `backend/.env` and add your `GEMINI_API_KEY`.
2.  **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```
3.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 📂 Project Structure

```
AI_Guruji/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints (Upload, Generate)
│   │   ├── services/     # Core Logic (RAG, TTS, Slides, Orchestrator)
│   │   └── core/         # Prompts & Config
│   └── data/             # Stores output media and vector DBs
├── frontend/
│   ├── src/
│   │   ├── components/   # Player & UI Components
│   │   └── App.jsx       # Main Application
└── implementation_plan.md
```

## ⚠️ Notes
*   **Avatar Generation**: Requires `wav2lip_gan.pth` weights and a GPU. See `README_AVATAR.md` for details.
*   **Time Control**: The system automatically calculates audio duration to sync slides perfectly.

---
Built with ❤️ by the AI Guruji Team.
