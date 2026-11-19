# PUCIT GPA & CGPA Assistant

An Agentic AI conversational assistant for PUCIT BS(CS) students. The assistant can calculate semester GPA, project CGPA, determine the GPA required to reach a target CGPA, retrieve semester course outlines, and save reports. Its tools are served over **MCP (Model Context Protocol)**, so any MCP-compatible client can use them.

## Live MCP Server

The tools are hosted as a remote MCP server (Streamable HTTP):

```text
https://pucit-gpa-cgpa-assistant-for-cs.onrender.com/mcp
```

- Opening this URL in a browser shows `405 Method Not Allowed`. This is expected: browsers send GET requests, while MCP only accepts POST.
- On a free hosting tier the server may sleep when idle, so the first request can take a while to respond.
- Any MCP-compatible client or agent can connect to this URL and discover the tools through `tools/list`.

## Features

- Calculate semester GPA from marks.
- Convert marks into grade points according to the provided grading scheme.
- Calculate projected CGPA after a semester.
- Calculate the GPA required to achieve a target CGPA.
- Handle unreachable targets by extending the calculation horizon to subsequent semesters.
- Retrieve course outlines and credit hours for semesters 1–8.
- Save meaningful GPA/CGPA results as reports when explicitly requested.
- Conversational interaction with missing-information handling.
- Tools exposed through an MCP server, consumed by the agent as an MCP client.
- Persistent chat memory: every user has their own saved conversation (thread), kept across restarts.
- Streaming responses with live tool-call visibility.
- Graceful handling of an unreachable MCP server (the model is told the tool failed instead of the chat crashing).
- Streamlit web interface for interacting with the agent.

## Project Structure

```text
AI Assignment/
│
├── app.py          # Streamlit interface
├── agent.py        # MCP client + agent + persistent memory + streaming chat loop
├── tools.py        # GPA/CGPA tools, exposed through the MCP server
├── server.py       # MCP server entry point
├── llm.py          # LLM configuration
├── chats.db        # SQLite chat memory (created automatically, not committed)
├── .env.example
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- LangChain (`langchain.mcp.MCPAdapter`, `create_agent`)
- FastMCP (MCP server)
- LangGraph SQLite checkpointer (`AsyncSqliteSaver`)
- Streamlit
- Groq
- Python-dotenv

## Agent Architecture

The project follows a tool-based agent architecture, with the tools living behind an MCP server:

```text
User
  ↓
Streamlit Interface / Terminal Chat
  ↓
Host: LangChain Agent + LLM
  ↓
MCP Client (MCPAdapter)  ←→  SQLite checkpointer (per-user memory)
  ↓  tools/list, tools/call (Streamable HTTP)
MCP Server (hosted)
  ├── Marks → Grade Points
  ├── Semester GPA
  ├── New CGPA
  ├── Required GPA
  ├── Semester Courses
  ├── Remaining Credit Hours
  └── Save Report
```

The LLM is responsible for understanding the user's request and deciding which tool should be used. Numerical calculations are performed by the tools rather than by the language model. The MCP server never sees the LLM; it only answers the client's tool calls.

## Grading Scheme

|    Marks | Grade | Grade Points |
| -------: | :---: | -----------: |
|      85+ |   A   |          4.0 |
|    80–84 |  A-   |          3.7 |
|    75–79 |  B+   |          3.3 |
|    70–74 |   B   |          3.0 |
|    65–69 |  B-   |          2.7 |
|    61–64 |  C+   |          2.3 |
|    58–60 |   C   |          2.0 |
|    55–57 |  C-   |          1.7 |
|    50–54 |   D   |          1.0 |
| Below 50 |   F   |          0.0 |

MD-001 and MD-002 are treated as non-credit pass/fail courses and are excluded from GPA calculations. Quran Translation courses carry 0.5 credit hours.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI\ Assignment
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -U "langchain[mcp]" langchain-groq langgraph-checkpoint-sqlite aiosqlite streamlit python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
LLM_MODEL=groq:openai/gpt-oss-20b
API_KEY=your_groq_api_key_here
MCP_URL=https://pucit-gpa-cgpa-assistant-for-cs.onrender.com/mcp
```

For local development, run the MCP server yourself and point `MCP_URL` to it:

```env
MCP_URL=http://127.0.0.1:8000/mcp
```

If `MCP_URL` is not set, the agent defaults to `http://127.0.0.1:8000/mcp`.

Do not commit the `.env` file to GitHub. A `.env.example` file is included as a template.

## Running the Application

### Terminal chat (agent.py)

If you use the local server, start it first in a separate terminal:

```powershell
python server.py
```

Then start the chat:

```powershell
python agent.py
```

The chat lists the saved conversations, asks who is chatting (the name becomes the thread id), and supports these commands:

| Command    | Action                                         |
| ---------- | ---------------------------------------------- |
| `/switch`  | Change to another person's conversation        |
| `/history` | Show the saved messages of the current person  |
| `/forget`  | Delete the current person's saved conversation |
| `/exit`    | Quit                                           |

Replies stream in as they are generated, and each tool call and its result are shown while the agent works.

### Streamlit interface

```powershell
streamlit run app.py
```

Streamlit will provide a local URL where the GPA & CGPA Assistant can be used.

## Example Queries

```text
Give me the course outline for semester 5.

Calculate my semester 5 GPA from my marks.

My current CGPA is 3.12 and I have completed 67 credit hours.
What GPA do I need to reach 3.30?

Can I reach a CGPA of 3.80?

What grade point is 78 marks?
```

## Conversation State

Conversation memory is handled by a LangGraph checkpointer (`AsyncSqliteSaver`) backed by a local SQLite file (`chats.db`). After every step of the agent, the full state is saved under a thread id, which identifies whose conversation it is. On each turn only the new message is sent; the saved history for that thread is loaded and the new message is appended to it. Because the history is stored on disk, chats survive closing the program, and different users never see each other's messages.

## Reliability

If the MCP server is unreachable while a tool is being called, the failure is caught and returned to the model as a tool error message. The model then tells the user that the tools are unavailable instead of the chat crashing, and no unanswered tool call is left in the saved history (which would make most model APIs reject the conversation).

## Important Design Rules

- The agent does not invent missing marks, credit hours, CGPA, or semester information.
- Missing information is requested from the user when it cannot be obtained through an available tool.
- Only one or two missing pieces of information are requested at a time.
- Numerical calculations are delegated to the appropriate tools.
- Required GPAs above 4.0 are treated as unreachable for that calculation horizon.
- The calculation horizon can be extended across subsequent semesters when required.
- Reports are saved only after the user explicitly requests them.

## Assignment Scope

The project implements the required GPA/CGPA agent, an MCP-based tool layer, persistent per-user memory, streaming output, and a Streamlit interface. Repeated-course improvements, relative grading, incomplete/withdrawal cases, and other features outside the specified assignment requirements are not included.
