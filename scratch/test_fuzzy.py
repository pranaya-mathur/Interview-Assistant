import asyncio
import os
import sys

# Set standard paths
sys.path.append(os.getcwd())
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]

from router.question_router import QuestionRouter

async def test_govgig_fuzzy():
    print("🎭 TEST: GovGig Fuzzy Matching")
    router = QuestionRouter()
    
    # Test case: Natural language mention of 'GovGig update'
    question = "Tell me something about the GovGig update your project."
    
    category, project_id = router.classify(question)
    
    print(f"\nQuestion: {question}")
    print(f"Detected Category: {category}")
    print(f"Detected Project ID: {project_id}")
    
    if project_id == "govgig_updated" or project_id == "govgig":
        print("\n✅ SUCCESS: Fuzzy matcher successfully identified the project.")
    else:
        print("\n❌ FAILURE: Project ID still undetected.")

if __name__ == "__main__":
    asyncio.run(test_govgig_fuzzy())
