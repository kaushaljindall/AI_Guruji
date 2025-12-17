import os
import torch
from TTS.api import TTS

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "data", "outputs", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/en/ljspeech/glow-tts" # Fast and decent quality
        # For higher quality/cloning, use: "tts_models/multilingual/multi-dataset/xtts_v2"
        
        print(f"Initializing Coqui TTS on {self.device}...")
        try:
            self.tts = TTS(self.model_name).to(self.device)
        except Exception as e:
            print(f"Error loading TTS model: {e}")
            self.tts = None

    def generate_audio(self, text: str, output_filename: str) -> tuple[str, float]:
        """
        Generates audio from text using Coqui TTS.
        Returns a tuple: (path_to_wav_file, duration_in_seconds)
        """
        if not self.tts:
            raise RuntimeError("TTS Model not initialized.")

        file_path = os.path.join(self.output_dir, output_filename)
        
        # Generate Audio
        self.tts.tts_to_file(text=text, file_path=file_path)
        
        # Calculate Duration
        import contextlib
        import wave
        
        duration = 0.0
        try:
            with contextlib.closing(wave.open(file_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
        except Exception as e:
            print(f"Error calculating duration for {file_path}: {e}")
            
        return file_path, duration

tts_service = TTSService()
