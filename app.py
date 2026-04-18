import os
import sys
import asyncio
import time
import json

# Ensure Homebrew path is included for ffmpeg and other binaries
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from audio.recorder import record_with_vad, list_audio_devices, SPEAK_OUTPUT
from stt.transcriber import transcribe_audio
from llm.answer_generator import ask_llm, speak_answer, extract_and_save_code
from router.question_router import QuestionRouter
from context.retrievers.memory_retriever import MemoryRetriever
from context.vector_store import VectorStore
from context.mcp_client import MCPClient
from context.retrievers.filesystem_retriever import FilesystemRetriever
from context.retrievers.github_retriever import GitHubRetriever
from context.retrievers.git_retriever import GitRetriever

async def run_interview_loop():
    print("\n" + "="*100)
    print("🎙️ PARAKEET AI v2.5 - MCP ORCHESTRATOR")
    print("→ Mode: HYBRID (Groq/Ollama) | Context: MCP Enabled")
    print("→ Quit: Ctrl + C")
    print("="*100)
    
    # Initialize devices
    list_audio_devices()
    
    # Initialize Core Components
    router = QuestionRouter()
    mcp_client = MCPClient()
    v_store = VectorStore() # New Vector Memory
    
    # Initialize Retrievers
    fs_retriever = FilesystemRetriever(mcp_client)
    gh_retriever = GitHubRetriever(mcp_client)
    git_retriever = GitRetriever(mcp_client)
    mem_retriever = MemoryRetriever(mcp_client)
    
    # Attempt to connect to MCP Servers (errors will be printed but not stop the loop)
    # Optimized: Run connections concurrently for near-instant boot
    print("🔌 Initializing persistent MCP sessions (Diagnostic Boot)...")
    try:
        await asyncio.gather(
            fs_retriever.connect(),
            gh_retriever.connect(),
            git_retriever.connect(),
            mem_retriever.connect()
        )
        print("✅ All MCP systems synchronized and warm.")
    except Exception as e:
        print(f"⚠️ MCP Startup Warning: {e}")

    # Start Heartbeat Task to keep sessions alive during long pauses
    async def heartbeat():
        while True:
            await asyncio.sleep(300) # Every 5 minutes
            try:
                # Minimal requests to keep servers warm
                await asyncio.gather(*[session.list_tools() for session in mcp_client.sessions.values()])
            except:
                pass
    
    asyncio.create_task(heartbeat())

    # 1. DYNAMIC HOTWORD PRIMING
    # Pull all project names from Memory Knowledge Graph for perfect STT recognition
    print("🧠 Priming Whisper with your project portfolio...")
    project_names = ["Nyaysetu", "GovGig", "SecureVU", "RAG", "MCP", "LangGraph", "Groq"]
    try:
        # Search for all "Project" typed entities in memory
        raw_graph = await mem_retriever.get_graph()
        # Heuristic: Find all names in the graph data
        import re
        names = re.findall(r'"name":\s*"([^"]+)"', str(raw_graph))
        if names:
            project_names.extend(names)
    except:
        pass
    
    # Standardize and deduplicate
    hotwords = ", ".join(sorted(list(set(project_names))))
    print(f"✅ Whisper biased towards {len(project_names)} project identifiers.")
    
    # Initialize Interview Memory (Short-term context)
    chat_history = []
    
    try:
        while True:
            # 1. Capture Audio
            audio = record_with_vad()
            if audio is None:
                continue
            
            print("\n📝 Question detected successfully!")
            
            # 2. Transcribe with Dynamic Hotwords
            question = transcribe_audio(audio, hotwords=hotwords)
            if not question:
                print("⚠️ Ignored (Noise or Hallucination)")
                continue
            
            print(f"📝 Question: {question}")
            
            # 3. Routing & Classification
            category, project_id = router.classify(question)
            print(f"🎯 Category: {category} | Project Target: {project_id if project_id else 'None'}")
            
            # 4. Context Retrieval (Selective Grounding + Vector Memory)
            context = await get_grounded_context(
                category, project_id, question, 
                fs_retriever, git_retriever, gh_retriever, mem_retriever, v_store
            )
            
            print("\n🤖 Generating grounded answer...")
            
            # 5. Generate Answer
            answer = ask_llm(question, context=context, history=chat_history)
            
            # Update Interview Memory
            chat_history.append({"Q": question, "A": answer})
            chat_history = chat_history[-4:] # Keep strictly last 4 exchanges

            
            print("\n" + "="*100)
            print("💡 SUGGESTED ANSWER:")
            print("="*100)
            print(answer)
            print("="*100)
            
            # 6. Extract Code Snippet (if any)
            is_code = extract_and_save_code(answer)
            if is_code:
                print("✨ Live coding snippet updated!")
            
            # 7. Output
            if SPEAK_OUTPUT:
                speak_answer(answer)
            
            # 8. Log Session
            log_session(question, answer, category)
            
            print("\n✅ Listening again...\n")
            
    except KeyboardInterrupt:
        print("\n\n✅ Script stopped. All the best Pranay! 💪")
    except Exception as e:
        print(f"\nCritical Error: {e}")
    finally:
        await mcp_client.disconnect_all()

async def get_grounded_context(category, project_id, question, fs, git, gh, mem, v_store):
    """Orchestrates selective retrieval based on question category and vector memory."""
    context_chunks = []
    
    # 1. SEMANTIC CODE SEARCH (The "Bigger Brain")
    # This instantly pulls relevant logic from any of the 24 projects
    print("🧠 Searching global vector memory...")
    try:
        code_matches = v_store.semantic_search(question, limit=3)
        for res in code_matches:
            context_chunks.append(f"CODE EVIDENCE (Repo: {res['repo']}, File: {res['path']}):\n{res['text']}")
    except Exception as e:
        print(f"⚠️ Vector Search Error: {e}")

    try:
        # 2. TARGETED PROJECT SEARCH: If a specific project was detected, go deep
        if project_id:
            print(f"🔍 Perform targeted search for: {project_id}")
            # Try to get the real project name from ID
            project_name = project_id.replace("_", "-")
            
            # Fetch from Memory Graph first (Project description/Key snippets)
            mem_data = await mem.search_memory(project_id)
            if mem_data and "entities" in str(mem_data):
                context_chunks.append(f"DEEP CONTEXT (Memory - {project_id}):\n{mem_data}")
            
            # Fetch from GitHub README for the most recent tech stack
            gh_data = await gh.get_project_context(project_name)
            if gh_data and "Error" not in gh_data:
                context_chunks.append(f"DEEP CONTEXT (GitHub - {project_name}):\n{gh_data[:2000]}")

        # 3. GENERAL CATEGORY RETRIEVAL
        if category == "RESUME":
            resume = await fs.get_prep_file("prep/resume.md")
            context_chunks.append(f"RESUME CONTEXT:\n{resume}")
            
        if category == "BEHAVIORAL":
            stars = await fs.get_prep_file("prep/star_stories.md")
            context_chunks.append(f"STAR STORIES:\n{stars}")

        if category == "CODING":
            # Search for real code implementations
            code_evidence = await gh.search_code(project_id if project_id else question)
            if code_evidence:
                context_chunks.append(f"PAST CODE IMPLEMENTATIONS:\n{code_evidence}")

    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        
    return "\n\n".join(context_chunks)

def log_session(question, answer, category):
    """Saves the interview Q&A to a local file."""
    try:
        log_file = "interview_notes.txt"
        with open(log_file, "a") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')} | CAT: {category}\n")
            f.write(f"QUESTION: {question}\n")
            f.write(f"ANSWER:\n{answer}\n")
            f.write(f"{'='*50}\n")
        print(f"💾 Saved to {log_file}")
    except Exception as e:
        print(f"⚠️ Failed to save notes: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_interview_loop())
    except KeyboardInterrupt:
        # Suppress messy traceback on Ctrl+C at the top level
        sys.exit(0)
