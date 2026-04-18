import sys
import os
from context.vector_store import VectorStore

def inspect():
    print("🔍 VECTOR DATABASE INSPECTOR")
    print("-" * 50)
    
    store = VectorStore()
    
    # 1. Show Collection Stats
    stats = store.client.get_collection(store.collection_name)
    print(f"📊 Total Chunks Indexed: {stats.points_count}")
    
    # 2. Random Sampling or Search
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n🔎 Searching for logic matching: '{query}'...")
        results = store.semantic_search(query, limit=3)
        
        if not results:
            print("❌ No matches found.")
            return

        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} (Score: Highly Relevant) ---")
            print(f"📂 Repo: {res['repo']} | 📄 File: {res['path']}")
            print(f"📝 Content Snippet:\n{res['text'][:300]}...")
            print("-" * 30)
    else:
        print("\n💡 Tip: Run 'python storage/inspect_vectors.py <query>' to test semantic search.")
        
if __name__ == "__main__":
    inspect()
