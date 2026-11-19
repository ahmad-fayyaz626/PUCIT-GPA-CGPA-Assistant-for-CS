# PUCIT GPA & CGPA Assistant

> **Live MCP server:** https://pucit-gpa-cgpa-assistant-for-cs.onrender.com/mcp

>**Github Link:** https://github.com/ahmad-fayyaz626/PUCIT-GPA-CGPA-Assistant-for-CS

> **How this repository is organized**
>
> - **Original assignment** (root files: `app.py`, `agent.py`, `tools.py`, `courses.py`): the GPA/CGPA agent with local tools and a Streamlit interface. This part is run with `streamlit run app.py`.
> - **MCP extension** (the `server/` and `agent/` folders): the same GPA/CGPA tools served over **MCP (Model Context Protocol)**, and a separate agent that connects to them as an MCP client, with persistent per-user memory, streaming, and tool-failure handling.

An Agentic AI conversational assistant for PUCIT BS(CS) students. The assistant can calculate semester GPA, project CGPA, determine the GPA required to reach a target CGPA, retrieve semester course outlines, and save reports.

## Features

- Calculate semester GPA from marks.
- Convert marks into grade points according to the provided grading scheme.
- Calculate projected CGPA after a semester.
- Calculate the GPA required to achieve a target CGPA.
- Handle unreachable targets by extending the calculation horizon to subsequent semesters.
- Retrieve course outlines and credit hours for semesters 1–8.
- Save meaningful GPA/CGPA results as reports when explicitly requested.
- Conversational interaction with missing-information handling.
- Streamlit web interface (original assignment).

Added by the MCP extension:

- Tools exposed through an MCP server, hosted online and reusable by any MCP-compatible client.
- An MCP client agent that discovers and calls those tools.
- Persistent chat memory: every user has their own saved conversation (thread) that survives restarts.
- Streaming responses with live tool-call visibility.
- Graceful handling of an unreachable MCP server.

## Project Structure

```text
PUCIT-GPA-CGPA-Assistant-for-CS/
│
├── app.py             # Streamlit interface (original assignment)
├── agent.py           # Agent with local tools (original assignment)
├── tools.py           # GPA/CGPA tools (original assignment)
├── courses.py         # Semester course outlines and credit hours
├── llm.py             # LLM configuration
│
├── server/            # MCP extension: MCP server exposing the tools
├── agent/             # MCP extension: MCP client agent (memory, streaming)
│
├── config/            # System prompt
├── reports/           # Saved reports
├── requirements.txt
├── .env               # Local secrets (not committed)
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- LangChain (`create_agent`, `langchain.mcp.MCPAdapter`)
- FastMCP (MCP server)
- LangGraph SQLite checkpointer (`AsyncSqliteSaver`)
- Streamlit
- Groq
- Python-dotenv

## Agent Architecture

### Original assignment

```text
User
  ↓
Streamlit Interface
  ↓
LangChain Agent
  ↓
LLM
  ↓
Local Tools
```

### MCP extension

```text
User (terminal chat)
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

## Live MCP Server

The tools are hosted as a remote MCP server (Streamable HTTP):

```text
https://pucit-gpa-cgpa-assistant-for-cs.onrender.com/mcp
```

- Opening this URL in a browser shows `405 Method Not Allowed`. This is expected: browsers send GET requests, while MCP only accepts POST.
- On a free hosting tier the server may sleep when idle, so the first request can take a while to respond.
- Any MCP-compatible client or agent can connect to this URL and discover the tools through `tools/list`.

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
cd PUCIT-GPA-CGPA-Assistant-for-CS
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

The MCP extension additionally needs `langchain[mcp]`, `langgraph-checkpoint-sqlite` and `aiosqlite`.

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

If `MCP_URL` is not set, the MCP agent defaults to `http://127.0.0.1:8000/mcp`. Do not commit the `.env` file to GitHub.

## Running the Application

### Original assignment (Streamlit)

```powershell
streamlit run app.py
```

Streamlit will provide a local URL where the GPA & CGPA Assistant can be used.

### MCP extension (terminal chat)

If you use a local server, start it first in a separate terminal (from the project root):

```powershell
python server/server.py
```

Then start the MCP agent:

```powershell
python agent/agent.py
```

The chat lists the saved conversations, asks who is chatting (the name becomes the thread id), and supports these commands:

| Command    | Action                                         |
| ---------- | ---------------------------------------------- |
| `/switch`  | Change to another person's conversation        |
| `/history` | Show the saved messages of the current person  |
| `/forget`  | Delete the current person's saved conversation |
| `/exit`    | Quit                                           |

Replies stream in as they are generated, and each tool call and its result are shown while the agent works.

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

**Original assignment:** the agent itself is stateless between invocations. The application carries the conversation history and provides it to the agent again when a new message is processed. Streamlit's `st.session_state` maintains the current conversation during the application session.

**MCP extension:** conversation memory is handled by a LangGraph checkpointer (`AsyncSqliteSaver`) backed by a local SQLite file (`chats.db`, created automatically). After every step of the agent, the full state is saved under a thread id, which identifies whose conversation it is. On each turn only the new message is sent; the saved history for that thread is loaded and the new message is appended to it. Chats therefore survive closing the program, and different users never see each other's messages.

## Reliability (MCP extension)

If the MCP server is unreachable while a tool is being called, the failure is caught and returned to the model as a tool error message. The model then tells the user that the tools are unavailable instead of the chat crashing, and no unanswered tool call is left in the saved history (which would make most model APIs reject the conversation).

## Important Design Rules

- The agent does not invent missing marks, credit hours, CGPA, or semester information.
- Missing information is requested from the user when it cannot be obtained through an available tool.
- Only one or two missing pieces of information are requested at a time.
- Numerical calculations are delegated to the appropriate tools.
- Required GPAs above 4.0 are treated as unreachable for that calculation horizon.
- The calculation horizon can be extended across subsequent semesters when required.
- Reports are saved only after the user explicitly requests them.
- Requests outside GPA/CGPA topics (such as programming help) are politely declined.

## Assignment Scope

The original assignment implements the required GPA/CGPA agent and Streamlit interface. The MCP extension adds a hosted MCP tool server and a separate MCP client agent with persistent per-user memory and streaming. Repeated-course improvements, relative grading, incomplete/withdrawal cases, and other features outside the specified requirements are not included.
