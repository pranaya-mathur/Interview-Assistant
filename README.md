# 🧠 Pranaya's Personal AI Copilot & Interview Architect

Welcome to my **Personal AI Copilot** – a production-grade, state-of-the-art AI assistant designed to serve as an omniscient brain for my entire personal project portfolio. Originally conceptualized as an AI interview companion, it has evolved into a hyper-aware, zero-latency coding assistant that holds the exact semantic memory of **24+ unique repositories**.

---

## 🌟 Key Capabilities

- **Omniscient Portfolio Grounding:** Operates on a high-performance **Qdrant Vector Database** storing over `6,900+` semantic, AST-aware code chunks from my personal GitHub projects. Ask about *any* proprietary implementation (like a PostgreSQL pgvector setup or a LangGraph RAG), and it will fetch the exact source logic in sub-seconds.
- **Agentic Hybrid Intelligence:** 
  - **The Researcher (Local):** Employs `qwen2.5-coder:14b` (via local Ollama) for deep code traversal and privacy-first local embedding.
  - **The Speaker (Cloud):** Leverages `llama-3.3-70b-versatile` (via Groq API) for instantaneous, highly articulate response generation, wrapped in a strict "Senior Engineer" persona.
- **Model Context Protocol (MCP) Mastery:** Deeply integrated into the GitHub APIs, local filesystems, and in-memory caches utilizing concurrent MCP connections. Features a rate-resilient "Deep Crawler" engine to recursively map cross-repository structures.
- **Distortion-Free Voice Pipeline:** Custom-hardened audio processing using `mlx-whisper`, equipped with logic to explicitly suppress common Whisper AI hallucinations and echo-loops.

## 🏗 System Architecture

1. **Ingestion Engine (`vector_sync.py`)**: A rate-resilient Deep Crawler that bypasses standard API throttling restrictions. It recursively scans organization repositories, performs language-specific semantic chunking via LangChain, and embeds logic into Qdrant using Ollama's `nomic-embed-text`.
2. **Context Orchestrator (`app.py`)**: The central nervous system dynamically classifying real-time spoken queries. It maps verbal concepts directly to specific technical namespaces and leverages the Vector DB for "code-evidence" insertion.
3. **Response Policy Layer (`answer_generator.py`)**: Employs stringent identity-guardrails ensuring the AI translates raw code logic into plain-English design decisions, strictly maintaining a 1st-person voice ("In my project, I implemented..."), bypassing standard conversational filler.

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **[Ollama](https://ollama.com)** installed globally. Ensure the following models are spun up:
  - `ollama pull nomic-embed-text`
  - `ollama pull qwen2.5-coder:14b`
  - `ollama pull phi3.5:latest` *(Optional for edge instances)*
- Node.js (for `@modelcontextprotocol/server-github` `npx` executions).

### Setup Instructions

**1. Clone & Environment Bootstrap**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure Secrets**
Create a `.env` file at the root and provide your API keys:
```env
GROQ_API_KEY=gsk_your_groq_key
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token
```

**3. Vectorize the Portfolio**
Run the Deep Crawler to ingest all repository logic into the Local Qdrant memory. *(Only required initially or upon adding new projects.)*
```bash
PYTHONPATH=. python storage/vector_sync.py
```

**4. Spin up the Copilot**
Initialize the dual-pipeline STT and Semantic Generation engines concurrently:
```bash
python main.py
```

## 🛠 Core Tech Stack

- **Memory & Embeddings:** Qdrant Client (Local HNSW Engine), Ollama (`nomic-embed-text`)
- **Generation:** Groq LLM API (`llama-3.3-70b-versatile`)
- **Connectivity:** Model Context Protocol (MCP)
- **Audio:** `mlx-whisper` (Text-to-Speech via native macOS `say`)
- **Data Engineering:** Langchain Text Splitters

## 📜 Disclaimer
This system is strictly designed to act as a technical extension of my memory for coding iterations and architectural discussions. The AI is hardcoded to extract professional project methodologies, explaining them succinctly without exposing raw code blocks to the audio generation pipeline.
