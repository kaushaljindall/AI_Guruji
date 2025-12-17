import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, Loader } from 'lucide-react';
import Player from './components/Player';

function App() {
    const [file, setFile] = useState(null);
    const [viewMode, setViewMode] = useState("upload"); // upload | player
    const [uploadStatus, setUploadStatus] = useState("idle"); // idle, uploading, success, error
    const [ingestionData, setIngestionData] = useState(null);
    const [lectureData, setLectureData] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploadStatus("uploading");

        const formData = new FormData();
        formData.append("file", file);

        try {
            // Assuming backend is on port 8000
            const response = await axios.post("http://127.0.0.1:8000/api/upload-pdf", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setIngestionData(response.data);
            setUploadStatus("success");
        } catch (error) {
            console.error(error);
            setUploadStatus("error");
        }
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            // Assuming the topic is derived from the PDF or static for now
            const response = await axios.post("http://127.0.0.1:8000/api/generate-lecture-plan", {
                topic: "Uploaded Document Context"
            }, {
                timeout: 300000 // 5 minutes timeout for long generation
            });
            console.log("Generation Result:", response.data);
            setLectureData(response.data.pipeline_results);
            setIsGenerating(false);
            setViewMode('player');
        } catch (error) {
            console.error("Generation failed:", error);
            setIsGenerating(false);
            alert("Failed to generate lecture. Check backend console.");
        }
    };

    if (viewMode === 'player' && lectureData) {
        return (
            <div className="min-h-screen bg-[#0f172a] text-white overflow-hidden">
                <Player
                    scenes={lectureData}
                />
                <button
                    onClick={() => setViewMode('upload')}
                    className="absolute top-6 left-6 text-slate-500 hover:text-white transition-colors z-50 font-semibold"
                >
                    &larr; Back to Upload
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
            <div className="w-full max-w-2xl bg-white/10 backdrop-blur-lg rounded-2xl p-10 shadow-2xl border border-white/20">
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 mb-6 text-center">
                    AI Guruji Teacher System
                </h1>

                <p className="text-slate-300 text-center mb-10 text-lg">
                    Upload your course material (PDF) to generate a professional AI lecture.
                </p>

                <div className="flex flex-col items-center space-y-6">
                    <label className="w-full h-32 flex flex-col items-center justify-center border-2 border-dashed border-slate-500 rounded-xl hover:border-blue-400 hover:bg-white/5 transition-all cursor-pointer group">
                        <Upload className="w-8 h-8 text-slate-400 group-hover:text-blue-400 mb-2 transition-colors" />
                        <span className="text-slate-400 group-hover:text-blue-300 transition-colors">
                            {file ? file.name : "Click to select a PDF"}
                        </span>
                        <input type="file" accept=".pdf" className="hidden" onChange={handleFileChange} />
                    </label>

                    <button
                        onClick={handleUpload}
                        disabled={!file || uploadStatus === "uploading"}
                        className={`w-full py-4 rounded-xl font-semibold text-lg transition-all transform active:scale-95 shadow-lg
              ${!file
                                ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                                : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 hover:shadow-blue-500/25"}
              flex items-center justify-center gap-2
            `}
                    >
                        {uploadStatus === "uploading" ? (
                            <>
                                <Loader className="w-5 h-5 animate-spin" />
                                Ingesting Content...
                            </>
                        ) : uploadStatus === "success" ? (
                            <>
                                <CheckCircle className="w-6 h-6" />
                                Uploaded Successfully
                            </>
                        ) : (
                            "Start Ingestion"
                        )}
                    </button>

                    {uploadStatus === "success" && ingestionData && (
                        <div className="w-full bg-green-500/10 border border-green-500/30 rounded-xl p-6 mt-4 animate-fade-in-up">
                            <h3 className="text-green-400 font-semibold mb-2 flex items-center gap-2">
                                <FileText className="w-5 h-5" />
                                Ingestion Report
                            </h3>
                            <p className="text-sm text-slate-300">
                                <span className="font-mono text-green-300">{ingestionData.chunks_count}</span> context chunks created and stored in vector database.
                            </p>
                            <div className="mt-4 pt-4 border-t border-white/10 flex justify-end">
                                <button
                                    onClick={handleGenerate}
                                    disabled={isGenerating}
                                    className="text-sm font-semibold text-blue-300 hover:text-white transition-colors flex items-center gap-2"
                                >
                                    {isGenerating ? (
                                        <>
                                            <Loader className="w-4 h-4 animate-spin" />
                                            Generating Lecture...
                                        </>
                                    ) : (
                                        <>Proceed to Lecture Generation &rarr;</>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {uploadStatus === "error" && (
                        <div className="w-full bg-red-500/10 border border-red-500/30 rounded-xl p-4 mt-4 text-red-300 text-center">
                            Failed to upload PDF. Please check backend connection.
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default App
