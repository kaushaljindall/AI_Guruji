import React, { Suspense, useRef, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import { Ziva } from './Ziva';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Loader, Play, Pause, SkipForward, SkipBack } from 'lucide-react';

function Show() {
    const { lectureId } = useParams();
    const navigate = useNavigate();

    // State
    const [lectureData, setLectureData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playTick, setPlayTick] = useState(0); // Triggers re-renders/updates for Ziva

    // Refs
    const audioRef = useRef(new Audio());

    // 1. Fetch Lecture Data
    useEffect(() => {
        const fetchLecture = async () => {
            if (!lectureId) return;
            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/lecture/${lectureId}`);
                if (response.data) {
                    setLectureData(response.data);
                    setLoading(false);
                }
            } catch (err) {
                console.error("Failed to fetch lecture:", err);
                alert("Lecture data not found.");
                navigate('/upload');
            }
        };
        fetchLecture();

        // Cleanup audio on unmount
        return () => {
            audioRef.current.pause();
            audioRef.current.src = "";
        };
    }, [lectureId, navigate]);

    // Derived State
    const slides = lectureData?.slides || [];
    const currentSlide = slides[currentSlideIndex];

    // 2. Audio & Auto-Advance Logic
    useEffect(() => {
        if (!currentSlide) return;

        const handleAudioEnd = () => {
            if (currentSlideIndex < slides.length - 1) {
                // Auto Advance
                setCurrentSlideIndex(prev => prev + 1);
            } else {
                // End of Lecture
                setIsPlaying(false);
            }
        };

        const setupAudio = async () => {
            // Use fallback sample if audio_url is missing or was set to fallback by backend
            const audioUrl = currentSlide.audio_url
                ? `http://127.0.0.1:8000${currentSlide.audio_url}`
                : '/sample.mp3';

            if (audioUrl) {
                audioRef.current.src = audioUrl;
                audioRef.current.addEventListener('ended', handleAudioEnd);

                // If it was already playing, start the new track immediately
                if (isPlaying) {
                    try {
                        const playPromise = audioRef.current.play();
                        if (playPromise !== undefined) {
                            playPromise.then(() => {
                                setPlayTick(t => t + 1); // Notify Avatar
                            }).catch(e => {
                                console.error("Autoplay blocked or failed:", e);
                                setIsPlaying(false);
                            });
                        }
                    } catch (e) {
                        console.error("Audio setup error:", e);
                    }
                }
            }
        };

        setupAudio();

        return () => {
            audioRef.current.removeEventListener('ended', handleAudioEnd);
            audioRef.current.pause();
        };

    }, [currentSlide, currentSlideIndex, slides.length]);

    // Handle Play/Pause toggle in current slide
    useEffect(() => {
        if (isPlaying) {
            audioRef.current.play().catch(e => console.log("Play interrupted", e));
        } else {
            audioRef.current.pause();
        }
    }, [isPlaying]);

    const handleNext = () => {
        if (currentSlideIndex < slides.length - 1) {
            setCurrentSlideIndex(prev => prev + 1);
            setIsPlaying(true); // Keep playing
        }
    };

    const handlePrev = () => {
        if (currentSlideIndex > 0) {
            setCurrentSlideIndex(prev => prev - 1);
            setIsPlaying(true);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">
                <Loader className="w-10 h-10 animate-spin text-blue-500 mb-4" />
                <span className="text-xl ml-4 font-semibold">Loading Lecture Room...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 overflow-hidden">
            {/* Header / Nav */}
            <div className="absolute top-6 left-6 z-50">
                <button
                    onClick={() => navigate('/upload')}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white font-semibold backdrop-blur-md transition-all flex items-center gap-2"
                >
                    &larr; Exit Class
                </button>
            </div>

            <div className="h-screen flex gap-6 pt-16 pb-6">

                {/* LEFT SIDE: Dynamic Slide Presentation */}
                <div className="flex-[2] flex flex-col gap-4 max-w-5xl">
                    {/* Slide Viewer */}
                    <div className="flex-1 bg-white rounded-2xl shadow-2xl overflow-hidden relative flex flex-col p-12 border-4 border-slate-200">
                        {/* Slide Content */}
                        <div className="flex-1 border-l-8 border-blue-500 pl-8 flex flex-col justify-center animate-fade-in">
                            <h2 className="text-4xl font-bold text-slate-800 mb-6 font-serif leading-tight">
                                {currentSlide.heading}
                            </h2>

                            {/* Summary */}
                            {currentSlide.summary && (
                                <p className="text-xl text-slate-600 mb-8 italic border-b pb-4">
                                    "{currentSlide.summary}"
                                </p>
                            )}

                            {/* Points */}
                            <div className="space-y-4">
                                {Array.isArray(currentSlide.important_points) ? (
                                    currentSlide.important_points.map((point, idx) => (
                                        <div key={idx} className="flex items-start gap-3">
                                            <span className="w-2 h-2 mt-2.5 rounded-full bg-blue-500 shrink-0" />
                                            <p className="text-lg text-slate-700 leading-relaxed font-medium">
                                                {point}
                                            </p>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-lg text-slate-700">{currentSlide.important_points}</p>
                                )}
                            </div>

                            {/* Code Snippet if Any */}
                            {currentSlide.code && (
                                <div className="mt-8 bg-slate-800 p-4 rounded-lg overflow-x-auto border border-slate-700 shadow-inner">
                                    <pre className="text-sm font-mono text-green-400">
                                        <code>{currentSlide.code}</code>
                                    </pre>
                                </div>
                            )}
                        </div>

                        {/* Footer / Slide Number */}
                        <div className="mt-auto pt-6 flex justify-between items-center text-slate-400">
                            <span className="font-bold text-blue-900 tracking-widest text-sm uppercase">AI GURUJI • LECTURE SERIES</span>
                            <span className="text-2xl font-bold text-slate-300">
                                {currentSlideIndex + 1} <span className="text-lg transform translate-y-[-4px] inline-block text-slate-400">/</span> {slides.length}
                            </span>
                        </div>
                    </div>

                    {/* Controls */}
                    <div className="h-20 bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 flex items-center justify-between px-8">
                        <div className="flex items-center gap-6">
                            <button onClick={handlePrev} className="p-3 hover:bg-white/10 rounded-full transition-colors text-white disabled:opacity-50" disabled={currentSlideIndex === 0}>
                                <SkipBack className="w-6 h-6" />
                            </button>

                            <button
                                onClick={() => setIsPlaying(!isPlaying)}
                                className="w-14 h-14 bg-white rounded-full flex items-center justify-center text-purple-900 hover:scale-105 transition-transform shadow-lg shadow-purple-500/20"
                            >
                                {isPlaying ? <Pause className="w-6 h-6 fill-current" /> : <Play className="w-6 h-6 fill-current translate-x-0.5" />}
                            </button>

                            <button onClick={handleNext} className="p-3 hover:bg-white/10 rounded-full transition-colors text-white disabled:opacity-50" disabled={currentSlideIndex === slides.length - 1}>
                                <SkipForward className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="hidden lg:block text-slate-300 text-sm font-medium">
                            Playing: <span className="text-white">{currentSlide.heading}</span>
                        </div>
                    </div>
                </div>

                {/* RIGHT SIDE: Avatar (Ziva) */}
                <div className="flex-1 min-w-[360px] flex flex-col">
                    <div className="flex-1 bg-slate-800/80 backdrop-blur-xl rounded-2xl border-2 border-white/10 shadow-2xl relative overflow-hidden">

                        {/* Status Light */}
                        <div className="absolute top-4 right-4 z-10 flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10 backdrop-blur-md">
                            <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                            <span className="text-xs font-bold text-slate-200 tracking-wider">LIVE</span>
                        </div>

                        <Canvas
                            camera={{ position: [0, 1.2, 3.2], fov: 45 }}
                            style={{ width: '100%', height: '100%' }}
                            shadows
                        >
                            <Suspense fallback={null}>
                                <ambientLight intensity={0.6} />
                                <spotLight position={[5, 10, 5]} angle={0.4} penumbra={1} intensity={1.5} castShadow />
                                <pointLight position={[-5, 5, -5]} intensity={0.5} color="#blue" />

                                <Ziva
                                    position={[0, -2.5, 0]}
                                    scale={1.8}
                                    audio={audioRef.current}
                                    playTick={playTick}
                                />
                                <Environment preset="city" />
                            </Suspense>
                        </Canvas>
                    </div>

                    {/* Transcript Box */}
                    <div className="mt-4 h-48 bg-black/40 backdrop-blur-md rounded-2xl p-6 border border-white/5 overflow-y-auto custom-scrollbar">
                        <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">Transcribed Audio</p>
                        <p className="text-slate-200 font-light leading-relaxed">
                            {currentSlide.script}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Show;
