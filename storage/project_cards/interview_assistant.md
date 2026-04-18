# Project Card: Interview-Assistant

- **Summary**: A real-time voice-to-voice interview copilot.
- **Problem**: Interviews are high-stakes; candidates need quick context retrieval without breaking eye contact or focus.
- **Architecture**: Modular Python service using MCP for context, Whisper for STT, and Groq/Ollama for reasoning.
- **Stack**: Python, FastMCP, Groq API, Ollama, mlx-whisper, SoundDevice.
- **Key Features**: VAD-based automatic listening, Hallucination filtering, Hybrid LLM mode (local + cloud), Notepad session logging.
- **Challenges**: Audio hardware latency on Mac, Whisper hallucinations in noisy rooms.
- **Trade-offs**: Local STT (privacy/latency) vs Cloud LLM (intelligence).
- **Impact**: Reduced response time by 80% using GROQ and MCP indexing.
- **Likely Questions**: "How do you handle audio latency?", "Tell me about the logic behind your hallucination filter."
