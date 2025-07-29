import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import logging
from mcp.client.sse import sse_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Define server parameters for stdio transport
        async with sse_client("http://localhost:8080/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()

                # Load MCP tools for LangChain
                logger.info("Loading MCP tools")
                tools = await load_mcp_tools(session)

                # Set up LLM (replace with your model and API key)
                model = ChatOpenAI(
                    model="gpt-4o",
                    api_key="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"  # Replace with your actual API key
                )
                logger.info("Initialized LLM")

                # Create LangChain ReAcT agent
                logger.info("Creating LangChain agent")
                agent = create_react_agent(model, tools)

                # Test query to call tools
                query = "provide me the weather report in CA?"
                logger.info(f"Invoking agent with query: {query}")
                response = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})

                # Extract the response content
                # Assuming response['messages'] is a list of AIMessage objects
                last_message = response['messages'][-1]
                if hasattr(last_message, 'content'):
                    response_content = last_message.content
                else:
                    response_content = str(last_message)  # Fallback for unexpected format
                logger.info(f"Agent response: {response_content}")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())