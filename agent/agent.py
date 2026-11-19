import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

load_dotenv()

mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
DB_PATH = str(Path(__file__).parent / "chats.db") 

SYSTEM_PROMPT = (
    "You are a GPA and CGPA assistant for PUCIT BS(CS) students. You can calculate "
    "semester GPA, projected CGPA, and required GPA for a target CGPA. You can also "
    "provide information about courses and credit hours. Please ask the user for any "
    "missing information before performing calculations."
)


def build_agent(tools, memory):
    return create_agent(
        llm, tools=tools, system_prompt=SYSTEM_PROMPT, checkpointer=memory
    )


async def list_threads(memory):  # task point 1
    names = set()
    async for c in memory.alist(None):
        names.add(c.config["configurable"]["thread_id"])
    return sorted(names)


async def show_history(agent, config):  # /history
    state = await agent.aget_state(config)
    msgs = state.values.get("messages", [])
    shown = [m for m in msgs if m.type in ("human", "ai") and m.text]
    if not shown:
        print("(no history)")
    for m in shown:
        print(f"  {m.type}: {m.text}")


async def stream_turn(agent, text, config):
    inputs = {"messages": [HumanMessage(text)]}
    typing = False

    async for chunk in agent.astream(
        inputs, config, stream_mode=["updates", "messages"], version="v2"
    ):
        if chunk["type"] == "messages": 
            token, metadata = chunk["data"]
            if metadata["langgraph_node"] == "model" and token.text:
                if not typing:
                    print("Agent: ", end="", flush=True)
                    typing = True
                print(token.text, end="", flush=True)

        elif chunk["type"] == "updates": 
            for node, update in chunk["data"].items():
                if not update or "messages" not in update:
                    continue
                msg = update["messages"][-1]
                if node == "model" and msg.tool_calls:
                    if typing:
                        print()
                        typing = False
                    for call in msg.tool_calls:
                        print(f"  [model asks for] {call['name']}({call['args']})")
                elif node == "tools":
                    print(f"  [tool {msg.name} returned] {str(msg.content)[:100]}")

    if typing:
        print()


async def ask(prompt):  # input() event loop ko block na kare
    return (await asyncio.to_thread(input, prompt)).strip()


async def main():
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory, MCPAdapter(
        mcp_url
    ) as adapter:

        tools = await adapter.list_tools()
        agent = build_agent(tools, memory)

        print("Saved chats:", await list_threads(memory) or "none yet")
        name = await ask("Who is chatting? ")
        print("Commands: /switch  /history  /forget  /exit")

        while True:
            text = await ask(f"{name}: ")
            if not text:
                continue
            if text == "/exit":
                break
            if text == "/switch":
                name = await ask("Who is chatting now? ")
                continue

            config = {"configurable": {"thread_id": name}}

            if text == "/history":
                await show_history(agent, config)
                continue
            if text == "/forget":
                await memory.adelete_thread(name)
                print(f"Forgot {name}.")
                continue

            await stream_turn(agent, text, config)


if __name__ == "__main__":
    asyncio.run(main())
