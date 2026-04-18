import os
import sys

# Ensure we can import from the root
sys.path.append(os.getcwd())

from router.question_router import QuestionRouter
from llm.answer_generator import extract_and_save_code

def test_coding_flow():
    print("🧪 Testing Coding Flow...")
    router = QuestionRouter()
    
    # 1. Test Classification
    q = "Can you write a binary search in Python?"
    category = router.classify(q)
    print(f"Question: {q}")
    print(f"Detected Category: {category}")
    
    # 2. Test Extraction
    dummy_answer = """
Sure! Here is a binary search:
```python
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (high + low) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return -1
```
I implemented this in my algorithms repo.
    """
    success = extract_and_save_code(dummy_answer)
    print(f"Extraction Successful: {success}")
    
    if success and os.path.exists("storage/coding_snippet.py"):
        with open("storage/coding_snippet.py", "r") as f:
            content = f.read()
            print("--- Snippet Content ---")
            print(content)
            print("-----------------------")
    else:
        print("❌ FAILED: Snippet not found or extraction failed.")

if __name__ == "__main__":
    test_coding_flow()
