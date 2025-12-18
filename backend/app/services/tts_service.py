import os
import contextlib
import wave
import math

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "data", "outputs", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        self.tts = None
        
        try:
            import torch
            from TTS.api import TTS
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model_name = "tts_models/en/ljspeech/glow-tts"
            print(f"Initializing Coqui TTS on {self.device}...")
            self.tts = TTS(self.model_name).to(self.device)
            print("✅ Coqui TTS Initialized.")
        except Exception as e:
            print(f"⚠️ TTS Initialization Failed (Import/Model error): {e}")
            print("➡️ Audio will be SILENT (Mock Mode).")
            self.tts = None

    def generate_audio(self, text: str, output_filename: str) -> tuple[str, float]:
        """
        Generates audio from text using Multi-Provider Strategy:
        1. Coqui TTS (Best Quality, Local)
        2. gTTS (Google Cloud, Free tier, Reliable)
        3. Silent (Fallback)
        """
        file_path = os.path.join(self.output_dir, output_filename)
        
        # Strategy 1: Coqui TTS
        if self.tts:
            try:
                self.tts.tts_to_file(text=text, file_path=file_path)
                return self._get_wav_duration(file_path)
            except Exception as e:
                print(f"⚠️ Coqui TTS Failed: {e}. Switching to Backup...")
        
        # Strategy 2: gTTS (Google Text-to-Speech)
        try:
            print(f"🔄 Attempting gTTS for '{output_filename}'...")
            from gtts import gTTS
            from pydub import AudioSegment
            
            # gTTS generates MP3, we need WAV
            mp3_path = file_path.replace(".wav", ".mp3")
            tts = gTTS(text=text, lang='en')
            tts.save(mp3_path)
            
            # Convert to WAV
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(file_path, format="wav")
            
            # Allow clean up
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
                
            return self._get_wav_duration(file_path)

        except Exception as e:
            print(f"⚠️ gTTS Failed: {e}. Switching to Silent Mode...")

        # Strategy 3: Mock Fallback (Silent Audio)
        word_count = len(text.split())
        approx_duration = max(2.0, word_count / 2.3) # Minimum 2 seconds
        self._create_silent_wav(file_path, duration_sec=approx_duration)
        return file_path, approx_duration

    def _get_wav_duration(self, file_path: str) -> tuple[str, float]:
        """Helper to measure WAV duration."""
        try:
            with contextlib.closing(wave.open(file_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
            return file_path, duration
        except Exception as e:
            print(f"⚠️ Failed to read duration: {e}. Assuming 5s.")
            return file_path, 5.0

    def _create_silent_wav(self, file_path, duration_sec=1.0, sample_rate=22050):
        """Creates a silent wav file of given duration."""
        n_frames = int(sample_rate * duration_sec)
        # 16-bit silence is all 0s
        data = b'\x00\x00' * n_frames
        
        try:
            with wave.open(file_path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sample_rate)
                f.writeframes(data)
        except Exception as e:
            print(f"Failed to create silent wav: {e}")

tts_service = TTSService()
