import subprocess
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import mlx_whisper
import requests

# Set up GROQ client if API key is valid
groq_llm = None
if GROQ_API_KEY and GROQ_API_KEY != "your_api_key_here":
    try:
        groq_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            max_tokens=500 # Limit output for precision
        )
        print("⚡ GROQ Mode: ACTIVE (Instant Speed)")
    except Exception as e:
        print(f"⚠️ GROQ Init Error: {e}")
else:
    print("🏠 Local Mode: ACTIVE (Ollama)")

# ================== TUNING PARAMETERS (yahan change kar) ==================
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5
SILENCE_THRESHOLD = 0.015      # Increased to avoid noise triggering
MAX_QUESTION_DURATION = 45     # Thoda lamba sawal bhi chalega
SILENCE_TIMEOUT = 3.5          # 3.5 second silence = question khatam
DEBUG_VAD = True               # True rakh → RMS values dikhega (tuning ke liye)
SPEAK_OUTPUT = False           # Set to True if you want the AI to speak back
# =========================================================================

def is_speech(audio_chunk):
    rms = np.sqrt(np.mean(audio_chunk**2))
    if DEBUG_VAD:
        print(f"🔊 RMS: {rms:.4f}  → Speech: {rms > SILENCE_THRESHOLD}")
    return rms > SILENCE_THRESHOLD

def record_with_vad():
    print("\n🎙️ Listening automatically... (Interviewer bolna shuru karo)")
    audio_buffer = []
    silence_counter = 0
    speech_detected = False
    
    while True:
        chunk = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        chunk = chunk.flatten()
        audio_buffer.extend(chunk)
        
        if is_speech(chunk):
            speech_detected = True
            silence_counter = 0
        elif speech_detected:
            silence_counter += CHUNK_DURATION
        
        if speech_detected and silence_counter >= SILENCE_TIMEOUT:
            break
        if len(audio_buffer) / SAMPLE_RATE > MAX_QUESTION_DURATION:
            break
    
    if not speech_detected:
        return None
    return np.array(audio_buffer, dtype=np.float32)

def transcribe_audio(audio_array):
    temp_file = "temp_question.wav"
    wav.write(temp_file, SAMPLE_RATE, audio_array)
    
    # Prompting Whisper to expect technical AI/ML terms
    initial_prompt = "RAG, LLM, Inference, Latency, Tokens, PyTorch, Architecture, Vector Database, Pipeline."
    
    result = mlx_whisper.transcribe(
        temp_file, 
        path_or_hf_repo=MODEL_NAME, 
        language="en",
        initial_prompt=initial_prompt
    )
    if os.path.exists(temp_file):
        os.remove(temp_file)
    return result["text"].strip()

def ask_llm(question):
    prompt = f"""
You are a World-Class AI Lead/Architect (12+ years exp) for top-tier Indian & US tech companies.
The interviewer asked: "{question}"

Instructions:
1. Provide a direct, highly technical, and PRECISE answer in the first person.
2. BE CONCISE: Avoid unnecessary fluff or long introductions. Get straight to the technical core.
3. CONTEXTUAL AWARENESS: In this interview, "RAG" refers ONLY to Retrieval-Augmented Generation.
4. STRUCTURE: Use bullet points for trade-offs or components if it helps clarity.
5. Do NOT describe the question type. Answer in under 300 words.
"""
    # 1. Try GROQ for instant speed if available
    if groq_llm:
        try:
            response = groq_llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"⚠️ GROQ Error: {e} - Falling back to Ollama...")

    # 2. Fallback to Local Ollama
    try:
        res = requests.post("http://localhost:11434/api/generate",
                            json={
                                "model": "qwen2.5-coder:14b", 
                                "prompt": prompt.strip(), 
                                "stream": False,
                                "options": {"num_predict": 500} # Token limit for Ollama
                            },
                            timeout=120)
        return res.json()["response"].strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def speak_text(text):
    if text.startswith("ERROR:"):
        return # Don't speak errors
    
    # 'say' is built-in on Mac. Using 'Siri' or 'Samantha' for a premium feel.
    # We strip markdown for better speech.
    clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()
    try:
        print("🔊 Speaking answer...")
        subprocess.Popen(['say', '-v', 'Siri', clean_text])
    except:
        pass # Fallback if Siri voice is not downloaded

# ============== MAIN LOOP ==============
print("\n" + "="*100)
print("🎙️ PARAKEET AI v2.5 - HYBRID MODE (Ollama + GROQ)")
print("→ Mode: " + ("⚡ GROQ (Instant)" if groq_llm else "🏠 Local (Ollama)"))
print("→ Audio: Listening | Siri Output: " + ("ON" if SPEAK_OUTPUT else "OFF (Silent Mode)"))
print("→ Quit: Ctrl + C")
print("="*100)

print("\n🔄 Loading models...")
print("\n🎤 Available Audio Devices:")
print(sd.query_devices())
print(f"Using Default Input Device: {sd.default.device[0]}")

MODEL_NAME = "mlx-community/whisper-large-v3-turbo"

try:
    while True:
        audio = record_with_vad()
        if audio is None:
            continue
        
        print("\n📝 Question detected successfully!")
        question = transcribe_audio(audio)
        
        # --- Hallucination & Short Speech Filter (New & Improved) ---
        hallucinations = ["thank you", "thanks for watching", "subtitles by"]
        clean_q = question.lower().strip().replace(".", "")
        
        # If it's ONLY a hallucination, ignore.
        if clean_q in hallucinations or len(clean_q) < 5:
            print(f"⚠️ Ignored (Noise): {question}")
            continue
            
        # If it ends with a hallucination, just strip it but keep the question!
        for h in hallucinations:
            if question.lower().endswith(h):
                question = question[:-(len(h))].strip()
        
        print(f"📝 Question: {question}")
        print("\n🤖 Generating answer...")
        
        answer = ask_llm(question)
        
        print("\n" + "="*100)
        print("💡 SUGGESTED ANSWER:")
        print("="*100)
        print(answer)
        print("="*100)
        
        if SPEAK_OUTPUT:
            speak_text(answer) # <--- AB AI SIRF TAB BOLEGA JAB FLAG TRUE HO
        
        # --- Save to Notepad (interview_notes.txt) ---
        try:
            with open("interview_notes.txt", "a") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"QUESTION: {question}\n")
                f.write(f"ANSWER:\n{answer}\n")
                f.write(f"{'='*50}\n")
            print("💾 Saved to interview_notes.txt")
        except Exception as e:
            print(f"⚠️ Failed to save notes: {e}")
        
        print("\n✅ Listening again...\n")
        
except KeyboardInterrupt:
    print("\n\n✅ Script stopped. All the best Pranay! 💪")
except Exception as e:
    print(f"\nError: {e}")