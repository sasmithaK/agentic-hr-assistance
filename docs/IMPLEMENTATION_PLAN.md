# HR Candidate Screening Support Assistant (Multi-Agent System)
## Implementation Plan & Architecture Details

This document outlines the detailed architecture and implementation strategy designed to achieve **Excellent (90-100%)** marks according to the CTSE Assignment 2 criteria.

---

### 1. Problem Definition
HR teams manually screen resumes, compare them with job descriptions, identify skill gaps, and prepare summaries. This is repetitive, inconsistent, and time-consuming.

This system automates that workflow using a **4-agent pipeline**, where each agent performs a specialized task relying on explicit, real-world tools, and passes structured state to the next agent via **LangGraph**. The system supports both single-resume and batch-processing modes.

---

### 2. Multi-Agent Architecture (LangGraph)
The system uses **LangGraph** to construct a sequential, formal `StateGraph`.

**Workflow:**
`User Input` → `Agent 1 (Resume Parser)` → `Agent 2 (Job Matcher)` → `Agent 3 (Gap Analyzer)` → `Agent 4 (HR Decision)` → `Final Outputs`

**Conditional Routing:** If Agent 1 fails to extract data (e.g., corrupted file), LangGraph short-circuits execution and routes directly to `END`, preventing token wastage on downstream agents.

---

### 3. Agent Roles and Real-World Tools

#### Agent 1: Resume Parsing Agent (Sasmitha)
*   **Role:** Convert raw resume → structured JSON data.
*   **Tool:** `read_resume_pdf(filepath: str) -> str`
    *   *Real-World Action:* Reads local PDF files using `pypdf`. If standard extraction returns 0 characters, falls back to `pytesseract` OCR.
*   **Output to State:** Populates `candidate_profile` (name, skills, experience_years, role).

#### Agent 2: Job Matching Agent (Isara)
*   **Role:** Semantically compare candidate profile against the full Job Description.
*   **Tool:** `read_job_description(filepath: str) -> str`
    *   *Real-World Action:* Reads a plain-text `.txt` or `.md` JD file from the local file system. Enables flexible, context-aware matching rather than rigid keyword lookup.
*   **Output to State:** Populates `match_result` (match_score, matched_skills, missing_skills, reasoning).

#### Agent 3: Gap Analysis Agent (Olivea)
*   **Role:** Assess severity of skill gaps using web research.
*   **Tool:** `search_duckduckgo(query: str) -> List[Dict]`
    *   *Real-World Action:* Calls the free DuckDuckGo public API to find context about how important a missing skill is for the target role. Includes a graceful empty-result fallback.
*   **Output to State:** Populates `gap_analysis` (strengths, weaknesses, risk_level, analysis_summary).

#### Agent 4: HR Decision Agent (Dinithi)
*   **Role:** Synthesize all data into a final recommendation and generate batch reporting outputs.
*   **Tools:**
    *   `generate_pdf_report(state) -> str` — writes individual candidate PDF to the file system.
    *   `generate_ranked_csv(candidates) -> str` — aggregates batch results into a `pandas` DataFrame, sorts by match score, and saves `Master_Ranking_Overview.csv`.
    *   `generate_score_graphs(candidates) -> str` — uses `matplotlib` to produce a `Candidate_Scores_Chart.png` bar chart.
*   **Output to State:** Populates `final_output` (str).

---

### 4. Global State Design (LangGraph TypedDict)
State is passed using a strict Python `TypedDict`, ensuring absolutely zero context loss between nodes.

```python
from typing import TypedDict, Dict, Any, List

class AgentState(TypedDict):
    input_resume_path: str           # Provided by User
    job_description: str             # File path to the JD text file
    candidate_profile: Dict[str, Any]  # Populated by Agent 1
    match_result: Dict[str, Any]       # Populated by Agent 2 (must contain match_score: int)
    gap_analysis: Dict[str, Any]       # Populated by Agent 3
    final_output: str                  # Populated by Agent 4

class BatchState(TypedDict):
    candidates: List[AgentState]     # Aggregated results from the batch loop
    master_report_path: str
    graph_path: str
```

---

### 5. Technical Constraints: Zero-Cost & Local
This system **strictly prohibits** paid API keys.
*   **Engine:** All LangGraph nodes use `ChatOllama` communicating with a local Ollama server at `http://localhost:11434`.
*   **Recommended Models:** `phi3` (faster, 2.3GB) or `llama3:8b` (more accurate, 4.7GB).

---

### 6. CLI Interface
**Single Resume:**
```bash
python -m src.main --resume "local_data/input_resumes/cv.pdf" --jd "local_data/job_description/jd_software_engineer.txt"
```
**Batch Mode:**
```bash
python -m src.main --folder "local_data/input_resumes" --jd "local_data/job_description/jd_software_engineer.txt"
```

---

### 7. AgentOps & Observability (Logging)
All agents write structured traces to `execution_trace.log` using Python's `logging` module. Every log entry registers the agent name, tool invoked, inputs consumed, and outputs produced.

```python
logging.basicConfig(
    filename='execution_trace.log',
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
```

---

### 8. Evaluation Strategy (LLM-as-a-Judge)
The test suite uses a secondary local Ollama instance as an evaluator to check for hallucinations and structural integrity. Each student contributes specific test cases to the unified `tests/` harness.

---

### 9. Project Directory Structure
```text
agentic-hr-assistance/
├── src/
│   ├── main.py                  # Orchestrator, batch loop, CLI entry
│   ├── state/
│   │   └── graph_state.py       # AgentState & BatchState TypedDict
│   ├── utils/
│   │   └── logger.py            # Centralized observability logger
│   ├── agents/
│   │   ├── resume_agent.py      # Agent 1
│   │   ├── match_agent.py       # Agent 2
│   │   ├── gap_agent.py         # Agent 3
│   │   └── decision_agent.py    # Agent 4
│   └── tools/
│       ├── file_tools.py        # PDF reader (OCR fallback), JD reader, PDF writer
│       ├── search_tools.py      # DuckDuckGo web search + fallback
│       └── reporting_tools.py   # CSV ranking & Matplotlib chart generation
├── tests/
│   ├── llm_evaluator.py
│   ├── test_agent_1.py
│   ├── test_agent_2.py
│   ├── test_agent_3.py
│   └── test_agent_4.py
├── local_data/
│   ├── input_resumes/           # Place candidate PDFs here
│   ├── output_reports/          # Individual PDFs, Master CSV, Chart PNG
│   └── jd_software_engineer.txt # Sample Job Description
├── docs/
├── execution_trace.log
└── requirements.txt
```


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
