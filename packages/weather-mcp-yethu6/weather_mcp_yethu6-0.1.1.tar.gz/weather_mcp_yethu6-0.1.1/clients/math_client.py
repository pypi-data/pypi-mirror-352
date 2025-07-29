# Create server parameters for stdio connection
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI


from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    google_api_key="AIzaSyDjGE1j1tUrRga-d7f5WRGfZkHPZeJryzQ"
  
)



async def main():
   async with MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["main.py"],
            "transport": "stdio",
        },
        "weather": {
            # make sure you start your weather server on port 8000
            "url": "http://localhost:8080/sse",
            "transport": "sse",
        }
    }
) as client:
    agent = create_react_agent(llm, client.get_tools())
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    # weather_response = await agent.ainvoke({"messages": "provide me the weather alert in CA?"})
    
    print("Math Response:", math_response["messages"][-1].content)
            
if __name__ == "__main__":      
    
    import asyncio
    asyncio.run(main())
        
        
