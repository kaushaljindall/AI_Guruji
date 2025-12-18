import os
import contextlib
import wave
import math

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "data", "outputs", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        self.tts = None
        
        # Optional: Initialize Coqui only if explicitly needed, but we rely on EdgeTTS now.
        # We leave this try-block just in case `edge-tts` fails and we fall back.
        try:
            import torch
            from TTS.api import TTS
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model_name = "tts_models/en/ljspeech/glow-tts"
            # print(f"Initializing Coqui TTS on {self.device}...")
            # self.tts = TTS(self.model_name).to(self.device)
            # print("✅ Coqui TTS Initialized (Backup).")
        except Exception as e:
            # print(f"⚠️ Coqui TTS skipped: {e}")
            self.tts = None

    def generate_audio(self, text: str, output_filename: str) -> tuple[str, float]:
        """
        Generates audio Robustly using Multi-Provider Strategy (Cascade):
        1. Edge TTS (Microsoft Neural - Best Free Quality)
        2. Coqui TTS (Local Fallback)
        3. gTTS (Google Cloud Fallback)
        4. Silent/Mock (Ultimate failsafe)
        """
        # Ensure filename ends in mp3
        if not output_filename.endswith(".mp3"):
            output_filename = output_filename.rsplit('.', 1)[0] + ".mp3"
            
        file_path = os.path.join(self.output_dir, output_filename)
        
        # --- ATTEMPT 1: Edge TTS (High Quality, Online) ---
        try:
            # print(f"🎙️ Generating with Edge TTS for {output_filename}...")
            import subprocess
            voice = "en-US-JennyNeural" 
            
            cmd = ["edge-tts", "--text", text, "--write-media", file_path, "--voice", voice]
            
            # Run blocking
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                 print(f"✅ [Slide TTS] Generated with EdgeTTS (Microsoft Neural): {output_filename}")
                 return self._get_mp3_duration(file_path)
            else:
                 raise Exception("File not created by edge-tts")
                 
        except Exception as e:
            print(f"⚠️ [Slide TTS] Edge TTS Failed: {e}. Switching to Coqui...")

        # --- ATTEMPT 2: Coqui TTS ---
        if self.tts:
            try:
                # Coqui usually outputs wav by default
                wav_path = file_path.replace(".mp3", ".wav")
                self.tts.tts_to_file(text=text, file_path=wav_path)
                
                # Convert to MP3
                from pydub import AudioSegment
                sound = AudioSegment.from_wav(wav_path)
                sound.export(file_path, format="mp3")
                
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                    
                return self._get_mp3_duration(file_path)
            except Exception as e:
                print(f"⚠️ Coqui TTS Failed: {e}. Switching to gTTS...")
        
        # --- ATTEMPT 3: gTTS (Google TTS) ---
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(file_path) 
            return self._get_mp3_duration(file_path)

        except Exception as e:
            print(f"⚠️ gTTS Failed: {e}. Switching to Silent Mode...")

        # --- ATTEMPT 4: Silent Fallback ---
        print(f"🔇 Using Silent Fallback for {output_filename}")
        word_count = len(text.split())
        approx_duration = max(2.0, word_count / 2.5) 
        self._create_silent_mp3(file_path, duration_sec=approx_duration)
        return file_path, approx_duration
        
    def _get_mp3_duration(self, file_path: str) -> tuple[str, float]:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(file_path)
        return file_path, len(audio) / 1000.0

    def _create_silent_mp3(self, file_path: str, duration_sec: float):
        from pydub import AudioSegment
        silence = AudioSegment.silent(duration=int(duration_sec * 1000))
        silence.export(file_path, format="mp3")

    def _get_wav_duration(self, file_path: str) -> tuple[str, float]:
        """Helper to measure WAV duration."""
        try:
            with contextlib.closing(wave.open(file_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
            return file_path, duration
        except Exception as e:
            print(f"⚠️ Failed to reading wav duration: {e}")
            return file_path, 5.0

    def _create_silent_wav(self, file_path, duration_sec=1.0, sample_rate=22050):
        """Creates a silent wav file of given duration."""
        n_frames = int(sample_rate * duration_sec)
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
