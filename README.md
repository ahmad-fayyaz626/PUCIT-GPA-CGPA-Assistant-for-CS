# PUCIT GPA & CGPA Assistant

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
- Streamlit web interface for interacting with the agent.

## Project Structure

```text
AI Assignment/
│
├── app.py
├── agent.py
├── tools.py
├── llm.py
├── .env.example
├── .gitignore
└── README.md
```

## Technologies Used

- Python
- LangChain
- Streamlit
- Groq
- Python-dotenv

## Agent Architecture

The project follows a tool-based agent architecture:

```text
User
  ↓
Streamlit Interface
  ↓
LangChain Agent
  ↓
LLM
  ↓
Tools
  ├── Marks → Grade Points
  ├── Semester GPA
  ├── New CGPA
  ├── Required GPA
  ├── Semester Courses
  ├── Remaining Credit Hours
  └── Save Report
```

The LLM is responsible for understanding the user's request and deciding which tool should be used. Numerical calculations are performed by the tools rather than by the language model.

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

Install the required packages used by the project:

```powershell
pip install langchain langchain-groq streamlit python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
LLM_MODEL=groq:openai/gpt-oss-20b
API_KEY=your_groq_api_key_here
```

Do not commit the `.env` file to GitHub.

A `.env.example` file is included as a template.

## Running the Application

Start the Streamlit application with:

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

The agent itself is stateless between invocations. The application carries the conversation history and provides it to the agent again when a new message is processed.

Streamlit's `st.session_state` is used to maintain the current conversation during the application session.

## Important Design Rules

- The agent does not invent missing marks, credit hours, CGPA, or semester information.
- Missing information is requested from the user when it cannot be obtained through an available tool.
- Only one or two missing pieces of information are requested at a time.
- Numerical calculations are delegated to the appropriate tools.
- Required GPAs above 4.0 are treated as unreachable for that calculation horizon.
- The calculation horizon can be extended across subsequent semesters when required.
- Reports are saved only after the user explicitly requests them.

## Assignment Scope

The project implements the required GPA/CGPA agent and Streamlit interface. Persistent memory across application runs, repeated-course improvements, relative grading, incomplete/withdrawal cases, and other features outside the specified assignment requirements are not included.
