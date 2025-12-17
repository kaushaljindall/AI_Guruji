import React, { Suspense, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import { Ziva } from './Ziva';

function Show() {
    const audioRef = useRef(null);
    const [playTick, setPlayTick] = useState(0);

    const handlePlayAudio = () => {
        try {
            if (!audioRef.current) {
                audioRef.current = new Audio('/sample.mp3');
            }

            audioRef.current.currentTime = 0;
            audioRef.current.play().then(() => {
                setPlayTick((t) => t + 1);
            }).catch((e) => {
                console.error('Error playing audio:', e);
            });
        } catch (e) {
            console.error('Error initializing audio:', e);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="h-screen flex gap-6">
                {/* Left Side - Landscape Window for PPT Slides */}
                <div className="flex-1 flex items-center justify-center">
                    <div className="w-full h-[80vh] bg-slate-800/50 backdrop-blur-lg rounded-2xl border-2 border-white/20 shadow-2xl flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-6xl mb-4">📊</div>
                            <h2 className="text-2xl font-semibold text-white mb-2">Slide Window</h2>
                            <p className="text-slate-400">PPT slides will appear here</p>
                            <div className="mt-6 px-6 py-4 bg-slate-700/50 rounded-lg border border-white/10">
                                <p className="text-sm text-slate-300 italic leading-relaxed">
                                    "Hello! It is a sincere pleasure to meet you. I am delighted to assist you with any task or notion you have in mind. My goal is to be a reliable partner as we explore new ideas together. Whether you need to solve a problem or simply want to chat, I am ready to help. Let's embark on this journey and see what we can achieve!"
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Side - Portrait Window for 3D AI Model */}
                <div className="w-96 flex flex-col items-center justify-center gap-4">
                    <div className="w-full h-[80vh] bg-slate-800/50 backdrop-blur-lg rounded-2xl border-2 border-white/20 shadow-2xl overflow-hidden">
                        <Canvas
                            // Slightly closer, narrower FOV to frame upper body
                            camera={{ position: [0, 1.2, 3], fov: 50 }}
                            style={{ width: '100%', height: '100%' }}
                        >
                            <Suspense fallback={null}>
                                <ambientLight intensity={0.5} />
                                <directionalLight position={[5, 5, 5]} intensity={1} />
                                <spotLight position={[0, 10, 0]} angle={0.35} penumbra={1} intensity={1.1} />

                                {/* Position/scale tuned so only upper body is visible */}
                                <Ziva 
                                    position={[0, -2.6, 0]}
                                    scale={1.9}
                                    audio={audioRef.current}
                                    playTick={playTick}
                                />
                                
                                <Environment preset="sunset" />
                            </Suspense>
                        </Canvas>
                    </div>
                    
                    <button
                        onClick={handlePlayAudio}
                        className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors shadow-lg"
                    >
                        Play Sample Audio
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Show;
