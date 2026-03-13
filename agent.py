# agent.py — Agent orchestrator: MCP client + OpenAI tool-use loop
import asyncio
import sys
import json
from pathlib import Path
import nest_asyncio
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Allow asyncio.run() inside a running loop (needed in Jupyter)
nest_asyncio.apply()

MODEL = "gpt-4.1-mini"
SERVERS = {
    "weather": StdioServerParameters(command=sys.executable, args=["weather_server.py"]),
    "news":    StdioServerParameters(command=sys.executable, args=["news_server.py"]),
}

async def run_agent(user_message: str) -> str:
    """
    Run the full agent loop for one user message.
    Returns the assistant's final text response.
    """
    client = AsyncOpenAI()
    all_tools: list[dict] = []
    sessions: dict[str, ClientSession] = {}

    # --- Connect to all MCP servers and discover their tools ---
    context_managers = []
    for name, params in SERVERS.items():
        cm = stdio_client(params)
        context_managers.append((name, cm))

    # We need to keep the async context managers alive during the whole loop.
    # Build a simple helper that enters them all.
    async with stdio_client(SERVERS["weather"]) as (r_w, w_w), \
               stdio_client(SERVERS["news"])    as (r_n, w_n):

        async with ClientSession(r_w, w_w) as weather_session, \
                   ClientSession(r_n, w_n) as news_session:

            await weather_session.initialize()
            await news_session.initialize()
            sessions = {"weather": weather_session, "news": news_session}

            # Collect tools from all servers
            for server_name, session in sessions.items():
                tools_resp = await session.list_tools()
                for t in tools_resp.tools:
                    all_tools.append({
                        "name": t.name,
                        "description": t.description or "",
                        "input_schema": t.inputSchema,
                        "_server": server_name,   # track which server owns this tool
                    })

            # Build OpenAI-compatible tool list (no _server key)
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"],
                    },
                }
                for t in all_tools
            ]
            tool_to_server = {t["name"]: t["_server"] for t in all_tools}

            # --- Agentic tool-use loop ---
            messages = [{"role": "user", "content": user_message}]

            while True:
                response = await client.chat.completions.create(
                    model=MODEL,
                    tools=openai_tools,
                    messages=messages,
                )
                msg = response.choices[0].message

                # If no tool call → done
                if response.choices[0].finish_reason == "stop" or not msg.tool_calls:
                    return msg.content or ""

                # Add assistant message with tool_calls
                messages.append(msg)

                # Process tool calls
                for tc in msg.tool_calls:
                    server_name = tool_to_server[tc.function.name]
                    session = sessions[server_name]
                    args = json.loads(tc.function.arguments)
                    result = await session.call_tool(tc.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result.content[0].text if result.content else "",
                    })


def ask(question: str) -> str:
    """Synchronous wrapper — useful for testing and Streamlit."""
    return asyncio.run(run_agent(question))


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What's the weather in Paris and the top 5 news stories?"

    print(ask(q))
