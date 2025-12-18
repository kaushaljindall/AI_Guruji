import os
import subprocess
from gtts import gTTS
import time

TEXT = "This is a test of the audio generation system."
OUTPUT_DIR = "test_audio_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_edge_tts():
    print("\n--- Testing Edge TTS (Microsoft Neural) ---")
    filename = os.path.join(OUTPUT_DIR, "test_edge.mp3")
    if os.path.exists(filename): os.remove(filename)
    
    try:
        # Check if command exists
        # In some envs, 'edge-tts' might not be in PATH, so we try calling it as a python module if possible, 
        # or just hope the pip install put it in Scripts.
        print("   Running command: edge-tts --text ...")
        cmd = ["edge-tts", "--text", TEXT, "--write-media", filename, "--voice", "en-US-JennyNeural"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ EdgeTTS failed with exit code {result.returncode}")
            print(f"   Stderr: {result.stderr}")
            return False
            
        if os.path.exists(filename) and os.path.getsize(filename) > 100:
            print(f"✅ Success! File created: {filename} ({os.path.getsize(filename)} bytes)")
            return True
        else:
            print("❌ File created but looks empty/invalid.")
            return False
    except FileNotFoundError:
        print("❌ 'edge-tts' command not found. It might not be in your PATH.")
        print("   Try running: pip install edge-tts")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_gtts():
    print("\n--- Testing gTTS (Google) ---")
    filename = os.path.join(OUTPUT_DIR, "test_gtts.mp3")
    if os.path.exists(filename): os.remove(filename)
    
    try:
        tts = gTTS(text=TEXT, lang='en')
        tts.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 100:
            print(f"✅ Success! File created: {filename} ({os.path.getsize(filename)} bytes)")
            return True
        else:
            print("❌ File created but looks empty/invalid.")
            return False
    except Exception as e:
        print(f"❌ gTTS Failed: {e}")
        return False

if __name__ == "__main__":
    print("🔊 AUDIO PIPELINE DIAGNOSTIC 🔊")
    edge_ok = test_edge_tts()
    gtts_ok = test_gtts()
    
    print("\n--- SUMMARY ---")
    if edge_ok:
        print("✅ PRIMARY PROVIDER (EdgeTTS) IS WORKING.")
    elif gtts_ok:
        print("⚠️ PRIMARY FAILED, BUT FALLBACK (gTTS) IS WORKING.")
    else:
        print("❌ CRITICAL: NO TTS PROVIDERS WORKING. SYSTEM WILL USE MOCK/SILENT MODE.")
