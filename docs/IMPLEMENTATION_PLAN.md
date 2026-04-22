# HR Candidate Screening Support Assistant (Multi-Agent System)
## Implementation Plan & Architecture Details

This document outlines the detailed architecture and implementation strategy designed to achieve **Excellent (90-100%)** marks according to the CTSE Assignment 2 criteria.

---

### 1. Problem Definition (For Final Report)
HR teams manually screen resumes, compare them with job descriptions, identify skill gaps, and prepare summaries. This is repetitive, inconsistent, and time-consuming.
This system automates that workflow using a **4-agent pipeline**, where each agent performs a specialized task relying on explicit, real-world tools, and passes structured state to the next agent via LangGraph.

---

### 2. Multi-Agent Architecture (LangGraph)
The system uses **LangGraph** to construct a sequential, formal `StateGraph`.

**Workflow:**
 `User Input` -> `Agent 1` -> `Agent 2` -> `Agent 3` -> `Agent 4` -> `Final Output`

*Conditional Routing:* If Agent 1 fails to extract data (e.g., corrupted file), LangGraph will short-circuit the execution to avoid wasting context.

---

### 3. Agent Roles and Real-World Tools
Every student implements one agent and one distinct real-world tool with strict type hinting/docstrings.

#### Agent 1: Resume Parsing Agent
*   **Role:** Convert raw resume -> structured data.
*   **Tool:** `read_resume_pdf(filepath: str) -> str`
    *   *Real-World Action:* Interacts with the local file system to read raw strings from PDF/Docx files using `PyMuPDF`.
*   **Output to State:** Populates `candidate_profile` (name, skills, experience).

#### Agent 2: Job Matching Agent
*   **Role:** Compare candidate profile with role requirements.
*   **Tool:** `query_skills_db(job_title: str) -> list[str]`
    *   *Real-World Action:* Runs a `SELECT` statement on a local `hr_database.db` (SQLite) to retrieve standard skills for the role.
*   **Output to State:** Populates `match_score` and `matched_skills`.

#### Agent 3: Gap Analysis Agent
*   **Role:** Explain strengths & weaknesses/gaps.
*   **Tool:** `search_duckduckgo(query: str) -> list[dict]`
    *   *Real-World Action:* Uses a free API (e.g. DDG or Wikipedia) to check the validity or context of unfamiliar skills listed by the candidate.
*   **Output to State:** Populates `gap_analysis` (strengths, risk_level).

#### Agent 4: HR Decision Support Agent
*   **Role:** Generate final summary and decision.
*   **Tool:** `generate_pdf_report(state_dict: dict) -> str`
    *   *Real-World Action:* Writes text to `local_data/outputs/report.md`, interacting with the file-system.
*   **Output to State:** Final HR Decision text.

---

### 4. Global State Design (LangGraph TypedDict)
State is passed using a strict Python `TypedDict`, ensuring absolutely zero context loss between nodes.

```python
from typing import TypedDict, List

class AgentState(TypedDict):
    input_resume_path: str
    job_description: str
    candidate_profile: dict
    match_result: dict
    gap_analysis: dict
    final_output: str
```

---

### 5. Technical Constraints: Zero-Cost & Local
This system **strictly prohibits** the usage of paid APIs like OpenAI. 
*   **Engine:** The entire LangGraph framework will utilize `ChatOllama` communicating over `http://localhost:11434`.
*   **Suggested Models:** `llama3:8b` or `phi3`.

---

### 6. AgentOps & Observability (Logging)
To secure maximum observability marks, standard `print()` statements are bypassed in favor of Python's `logging` module. 

```python
import logging
logging.basicConfig(
    filename='execution_trace.log', 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```
Each agent executes a log registering the input consumed, the LLM token duration, the tool invoked, and the tool output.

---

### 7. Evaluation Strategy (LLM-as-a-Judge)
The test suite utilizes a secondary Ollama instance acting as an evaluator. This proves accuracy and secures maximum marks in Testing & Evaluation.

**Test Example Script Concept:**
1. Execute the full Graph.
2. Load the output text.
3. Send it to an Evaluator Agent (Ollama) with the prompt: 
   *"Did the Gap Analysis Agent hallucinate any skills not found in the original resume? Answer YES or NO."*
4. Test asserts: `assert evaluator_response == "NO"`

---

### 8. Recommended Project Directory Structure
```text
project/
├── src/
│   ├── main.py              # Orchestrator & StateGraph initialization
│   ├── state/
│   │   └── graph_state.py   # Definition of AgentState TypedDict
│   ├── utils/
│   │   └── logger.py        # Centralized tracing logger
│   ├── agents/
│   │   ├── resume_agent.py
│   │   ├── match_agent.py
│   │   ├── gap_agent.py
│   │   └── decision_agent.py
│   └── tools/
│       ├── file_tools.py    
│       ├── database_tools.py 
│       └── search_tools.py  
├── tests/
│   ├── test_agent_1.py
│   ├── test_agent_2.py
│   ├── test_agent_3.py      # Contains LLM Evaluators
│   └── test_agent_4.py      
├── local_data/              # Explicit real-world data locations
│   ├── hr_database.db
│   ├── input_resumes/
│   └── output_reports/
├── execution_trace.log      
└── requirements.txt
```
