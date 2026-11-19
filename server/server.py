from fastmcp import FastMCP
from pathlib import Path
import os, sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools import tools

mcp = FastMCP("CGPA Assistant for PUCIT BS CS")

for t in tools:
    mcp.add_tool(t.func)

port = int(os.getenv("PORT", 8000))


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=port)
