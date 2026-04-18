import os
import mlx_whisper
import scipy.io.wavfile as wav

MODEL_NAME = "mlx-community/whisper-large-v3-turbo"
HALLUCINATIONS = [
    "thank you", "thanks for watching", "subtitles by", "i am sorry", 
    "i'm so sorry", "please subscribe", "i'll see you in the next video"
]

def transcribe_audio(audio_array, sample_rate=16000, hotwords=""):
    """Transcribes audio array with dynamic hotword biasing (Nyaysetu, GovGig, etc.)."""
    temp_file = "temp_question.wav"
    try:
        wav.write(temp_file, sample_rate, audio_array)
        
        # Merge general AI terms with user-specific project names
        base_prompt = "RAG, LLM, Inference, Latency, Architecture, Python, "
        full_prompt = base_prompt + hotwords
        
        result = mlx_whisper.transcribe(
            temp_file, 
            path_or_hf_repo=MODEL_NAME, 
            language="en",
            initial_prompt=full_prompt
        )
        text = result["text"].strip()
        
        # Clean up hallucinations
        cleaned_text = filter_hallucinations(text)
        return cleaned_text
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def filter_hallucinations(text):
    """Filters out common Whisper hallucinations and repetitive noise loops."""
    if not text:
        return ""
        
    # 1. PHRASE REPETITION FILTER (Catch loops like "I'm sorry I'm sorry...")
    lower_text = text.lower()
    for h in HALLUCINATIONS:
        # If the hallucination phrase appears more than twice in the text, it's a loop
        if lower_text.count(h) >= 2 and len(text) < 150:
            print(f"⚠️ Hallucination loop suppressed: '{h}'")
            return ""

    # 2. WORD REPETITION FILTER (Catch stuttering noise)
    words = text.split()
    if len(words) > 8:
        word_counts = {}
        for w in words:
            word_counts[w.lower()] = word_counts.get(w.lower(), 0) + 1
        
        most_common_count = max(word_counts.values())
        # If more than 40% of the sentence is the same word
        if most_common_count / len(words) > 0.4:
            print("⚠️ Repetition noise detected. Discarding.")
            return ""

    # 3. SHORT NOISE FILTER
    clean_text = text.lower().strip().replace(".", "").replace("!", "")
    if clean_text in HALLUCINATIONS or len(clean_text) < 5:
        return ""
            
    return text
