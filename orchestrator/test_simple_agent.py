import asyncio
from app.core.llm_manager import llm_manager
from langchain_core.messages import SystemMessage, HumanMessage

async def test_simple_agent():
    try:
        print("Testing simple agent call...")
        llm = llm_manager.get_llm("deepseek", temperature=0.0)
        
        messages = [
            SystemMessage(content="You are a helpful assistant. Respond with just 'OK'."),
            HumanMessage(content="Hello")
        ]
        
        result = await llm.ainvoke(messages)
        print(f"Success: {result.content[:50]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_agent())
    print(f"Test {'PASSED' if success else 'FAILED'}")