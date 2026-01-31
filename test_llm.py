import asyncio
import sys
sys.path.append('orchestrator')

from orchestrator.app.core.llm_manager import llm_manager

async def test_llm():
    try:
        llm = llm_manager.get_llm("deepseek", temperature=0.0)
        result = await llm.ainvoke("Hello, respond with just 'OK'")
        print(f"LLM Response: {result.content}")
        return True
    except Exception as e:
        print(f"LLM Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm())
    print(f"Test {'PASSED' if success else 'FAILED'}")