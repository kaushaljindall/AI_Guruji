import React, { useState, useEffect, Suspense } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, Loader, PlayCircle } from 'lucide-react';
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import Show from './components/Show';
import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import { Ziva } from './components/Ziva';

function App() {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState("idle"); // idle, uploading, success, error
    const [ingestionData, setIngestionData] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [progress, setProgress] = useState(0);

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
            // Updated Endpoint
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
        setProgress(10); // Start

        // Simulate progress while waiting
        const progressInterval = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 90) return 90;
                return prev + 5;
            });
        }, 1000);

        try {
            // New Endpoint
            const response = await axios.post("http://127.0.0.1:8000/api/generate-lecture", {
                document_id: "latest", // Backend handles retrieval
                target_minutes: 10
            }, {
                timeout: 300000 // 5 minutes timeout
            });

            clearInterval(progressInterval);
            setProgress(100);

            console.log("Lecture Generated:", response.data);
            const lectureId = response.data.lecture_id;

            // Navigate to Show with ID
            setTimeout(() => {
                setIsGenerating(false);
                navigate(`/show/${lectureId}`);
            }, 500); // Brief pause to show 100%

        } catch (error) {
            console.error("Generation failed:", error);
            clearInterval(progressInterval);
            setIsGenerating(false);
            setProgress(0);
            alert("Failed to generate lecture. Please try again.");
        }
    };

    const UploadRoute = (
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
                                <span className="font-mono text-green-300">{ingestionData.chunks_count}</span> context chunks created.
                            </p>

                            <div className="mt-6 pt-6 border-t border-white/10">
                                {isGenerating ? (
                                    <div className="w-full flex flex-col items-center gap-6">
                                        {/* Avatar During Processing - Using Ziva */}
                                        <div className="w-48 h-48 rounded-full bg-slate-800/50 border-2 border-blue-500/30 overflow-hidden shadow-[0_0_20px_rgba(59,130,246,0.2)] relative">
                                            <Canvas
                                                camera={{ position: [0, 0.5, 3], fov: 40 }}
                                                style={{ width: '100%', height: '100%' }}
                                            >
                                                <Suspense fallback={null}>
                                                    <ambientLight intensity={0.7} />
                                                    <spotLight position={[5, 5, 5]} intensity={1} />
                                                    <Ziva
                                                        position={[0, -2.2, 0]}
                                                        scale={1.6}
                                                        audio={null}
                                                        playTick={0}
                                                    />
                                                    <Environment preset="city" />
                                                </Suspense>
                                            </Canvas>
                                        </div>

                                        <div className="w-full">
                                            <div className="flex justify-between mb-2 text-sm text-blue-300">
                                                <span className="animate-pulse">Teacher is preparing your class...</span>
                                                <span className="font-mono">{progress}%</span>
                                            </div>
                                            <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden shadow-inner">
                                                <div
                                                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-300 ease-out"
                                                    style={{ width: `${progress}%` }}
                                                ></div>
                                            </div>
                                            <p className="text-xs text-slate-500 mt-2 text-center italic">
                                                "I'm reviewing your document and crafting the perfect explanation."
                                            </p>
                                        </div>
                                    </div>
                                ) : (
                                    <button
                                        onClick={handleGenerate}
                                        className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg hover:shadow-blue-500/25"
                                    >
                                        <PlayCircle className="w-5 h-5" />
                                        Generate & Start Lecture
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {uploadStatus === "error" && (
                        <div className="w-full bg-red-500/10 border border-red-500/30 rounded-xl p-4 mt-4 text-red-300 text-center">
                            Failed to upload PDF. Please check backend.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={UploadRoute} />
            {/* New Show Route receiving lectureId */}
            <Route path="/show/:lectureId" element={<Show />} />
            <Route path="*" element={<Navigate to="/upload" replace />} />
        </Routes>
    );
}

export default App;

