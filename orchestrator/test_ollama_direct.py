import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def test_ollama_direct():
    try:
        llm = ChatOpenAI(
            base_url="http://localhost:11434/v1",
            model="deepseek-r1:latest",
            temperature=0.0,
            api_key="ollama",
        )
        
        print("Testing direct Ollama call...")
        result = await llm.ainvoke([HumanMessage(content="Hello, respond with just 'OK'")])
        print(f"Success: {result.content[:100]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama_direct())
    print(f"Test {'PASSED' if success else 'FAILED'}")