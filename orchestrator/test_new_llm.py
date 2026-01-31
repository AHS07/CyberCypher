import asyncio
from app.core.llm_manager import llm_manager, simple_llm_call

async def test_new_llm():
    try:
        print("Testing new direct Ollama LLM manager...")
        
        result = await simple_llm_call(
            "deepseek",
            "You are a helpful assistant. Respond with just 'OK'.",
            "Hello"
        )
        
        print(f"Success: {result[:50]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_new_llm())
    print(f"Test {'PASSED' if success else 'FAILED'}")