import sounddevice as sd
import numpy as np
import time

# Audio Configuration
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5
SILENCE_THRESHOLD = 0.030  # Increased to prevent false triggers from background noise
MAX_QUESTION_DURATION = 45
SILENCE_TIMEOUT = 3.5
DEBUG_VAD = True
SPEAK_OUTPUT = False

def is_speech(audio_chunk):
    """Detects if the given audio chunk contains speech based on RMS threshold."""
    rms = np.sqrt(np.mean(audio_chunk**2))
    if DEBUG_VAD:
        print(f"🔊 RMS: {rms:.4f}  → Speech: {rms > SILENCE_THRESHOLD}")
    return rms > SILENCE_THRESHOLD

def record_with_vad():
    """Records audio from the microphone using Voice Activity Detection (VAD)."""
    print("\n🎙️ Listening automatically... (Interviewer bolna shuru karo)")
    audio_buffer = []
    silence_counter = 0
    speech_detected = False
    
    while True:
        try:
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
        except Exception as e:
            print(f"⚠️ Audio Record Error: {e}")
            break
    
    if not speech_detected:
        return None
    return np.array(audio_buffer, dtype=np.float32)

def list_audio_devices():
    """Prints available audio devices and returns the default input device."""
    print("\n🎤 Available Audio Devices:")
    devices = sd.query_devices()
    print(devices)
    default_input = sd.default.device[0]
    print(f"Using Default Input Device: {default_input}")
    return default_input
