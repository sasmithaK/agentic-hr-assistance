# HR Candidate Screening Support Assistant 🤖📁

![Agentic AI Architecture](https://img.shields.io/badge/Architecture-LangGraph-blue)
![LLM Setup](https://img.shields.io/badge/LLM-Local_Ollama-green)
![Cost](https://img.shields.io/badge/Cloud_Cost-Zero-success)

A fully autonomous, multi-agent AI system developed to automate the HR candidate screening process. By leveraging a team of specialized AI agents acting in sequence, this system intakes raw candidate resumes, compares them against required job skillsets, performs a gap analysis, and generates a data-driven final hiring recommendation.

This project was developed for the **CTSE Assignment 2 – Machine Learning** and stringently hits all parameters regarding zero-cost execution, local inference, state management, and real-world tool use.

## 🚀 Key Features

*   **Multi-Agent Orchestration:** Powered by **LangGraph**, facilitating complex, state-aware routing between 4 distinct agent nodes.
*   **100% Local Inference:** Executes entirely on local hardware via **Ollama** (e.g., Llama 3 / Phi 3), guaranteeing zero cloud costs and total data privacy.
*   **Real-World System Interaction:** Agents utilize robust Python tools to interact with local files (parsing PDFs), local databases (SQLite), and external free-tier web APIs.
*   **Strict State Management:** Context is passed sequentially between agents utilizing LangGraph's strongly typed `State` object (TypedDict), preventing context dropout.
*   **AgentOps & Tracing:** Out-of-the-box LLM observability. System actions, token durations, and tool outputs are traced directly to `execution_trace.log`.
*   **LLM-as-a-Judge Evaluation:** Test suites evaluate the system's analytical agents using a secondary LLM pipeline to explicitly check for AI hallucinations.

## 👥 Team & Individual Contributions
*(Each team member designed 1 specific agent, 1 specific real-world tool, and evaluated their agent)*

| Team Member | Role / Agent Designed | Tool Implemented | Test Coverage Strategy |
| :--- | :--- | :--- | :--- |
| **Student 1** | Resume Parsing Agent | `read_resume_pdf(filepath)` | Accuracy Check on Parsed Entities |
| **Student 2** | Job Matching Agent | `query_skills_db(job)` | Job Matching Matrix Output |
| **Student 3** | Gap Analysis Agent | `search_web(query)` | LLM-as-a-judge (Hallucination check) |
| **Student 4** | HR Decision Agent | `generate_pdf_report(state)` | Output formatting assertion |

## 🏗️ Architecture & Workflow

The LangGraph architecture acts as a sequential processing pipeline. 
`User Input` ➔ `Parsing Agent` ➔ `Matching Agent` ➔ `Analysis Agent` ➔ `Decision Agent`

If any critical errors emerge (e.g., corrupted file in step 1), the LangGraph conditional edge immediately routes to the End State, bypassing unnecessary token expenditure. 

## 📂 Repository Structure

```text
project/
├── src/
│   ├── main.py              # LangGraph Workflow Orchestrator 
│   ├── state/
│   │   └── graph_state.py   # Global TypedDict state definition
│   ├── utils/
│   │   └── logger.py        # Central observability tracing
│   ├── agents/
│   │   ├── resume_agent.py  # Agent 1
│   │   ├── match_agent.py   # Agent 2
│   │   ├── gap_agent.py     # Agent 3
│   │   └── decision_agent.py# Agent 4
│   └── tools/
│       ├── file_tools.py    
│       ├── db_tools.py 
│       └── search_tools.py  
├── tests/
│   ├── llm_evaluator.py     # Setup for LLM-as-a-judge tests
│   └── test_agents.py
├── local_data/              
│   ├── hr_database.db       # Job skills constraints
│   ├── input_resumes/       # Place target PDFs here
│   └── output_reports/      # AI generated final decisions
├── requirements.txt
└── README.md
```

## ⚙️ Setup & Installation

### Prerequisites
1.  **Python 3.10+**
2.  **Ollama** installed on your local machine ([Download here](https://ollama.com/download)).

### Step 1: Install Dependencies
```bash
git clone <your-repo-link>
cd agentic-hr-assistance
pip install -r requirements.txt
```

### Step 2: Initialize Local LLM
Ensure Ollama is running in the background and pull your chosen small language model. The default for this system is `llama3:8b`.
```bash
ollama run llama3:8b
```

### Step 3: Scaffold Local Data
You will need to run the initial database setup to inject the reference job skills into the SQLite instance.
```bash
python scripts/db_scaffold.py
```

## 💻 Running the Application

Place a sample applicant resume (`.pdf`) into the `local_data/input_resumes/` folder, then trigger the LangGraph orchestration pipeline:

```bash
python src/main.py --resume "local_data/input_resumes/applicant_1.pdf" --job "Software Engineer"
```

The system will operate autonomously. You can view real-time traces inside `execution_trace.log`, and the final HR hire/reject summary will be output to `local_data/output_reports/`.

## 🧪 Testing

To run the property-based assertions and the LLM Evaluator scripts:
```bash
pytest tests/
```
*(Ensure Ollama is active during tests so the Evaluator LLM can judge system behavior).*
