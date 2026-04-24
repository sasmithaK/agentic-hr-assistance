# HR Candidate Screening Support Assistant 🤖📁

![Architecture](https://img.shields.io/badge/Architecture-LangGraph-blue)
![LLM](https://img.shields.io/badge/LLM-Local_Ollama-green)
![Cost](https://img.shields.io/badge/Cloud_Cost-Zero-success)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

A fully autonomous, locally-hosted **Multi-Agent System (MAS)** that automates the HR candidate screening process. A team of four specialized AI agents work in sequence to read resumes, semantically compare them to a Job Description file, identify skill gaps using web research, and produce a final hiring recommendation — complete with a ranked CSV overview and data visualizations.

> **CTSE Assignment 2 — SE4010 | Sri Lanka Institute of Information Technology**

---

## 🚀 What It Does

*   **📄 Reads Resumes:** Extracts text from candidate PDF resumes (with OCR fallback for image-based PDFs).
*   **📋 Reads Job Descriptions:** Parses a plain-text JD file, enabling semantic matching rather than rigid keyword lookup.
*   **🎯 Matches Skills Semantically:** Compares candidate profiles against the full JD context using a local LLM.
*   **🔍 Finds Gaps:** Uses real-time DuckDuckGo web search to assess the severity of missing skills.
*   **⚖️ Makes Decisions:** Generates individual PDF reports with a Hire / Interview / Reject recommendation.
*   **📊 Batch Processing:** Process an entire folder of resumes and receive a ranked `Master_Ranking_Overview.csv` and a visual `Candidate_Scores_Chart.png`.
*   **🔒 Free and Private:** Runs entirely locally via **Ollama** — no cloud API keys required.

---

## 👥 Team Contributions

Each member designed one agent, one real-world tool, and one automated test suite.

| Team Member | Agent Designed | Tool Implemented | Real-World Interaction | Testing Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Sasmitha** | Resume Parsing Agent | `read_resume_pdf` | File System (PDF + OCR) | LLM-as-a-Judge (hallucination check) |
| **Isara** | Job Matching Agent | `read_job_description` | File System (JD text file) | Property-based score assertion |
| **Olivea** | Gap Analysis Agent | `search_duckduckgo` | Free Public Web API | LLM-as-a-Judge (risk misclassification check) |
| **Dinithi** | HR Decision Agent | `generate_ranked_csv` + `generate_score_graphs` | File System (CSV + PNG write) | Output formatting & file creation assertion |

---

## 📂 Repository Structure

```text
agentic-hr-assistance/
├── src/
│   ├── main.py                  # LangGraph orchestrator & batch loop
│   ├── state/
│   │   └── graph_state.py       # AgentState & BatchState TypedDict
│   ├── utils/
│   │   └── logger.py            # Centralized observability logger
│   ├── agents/
│   │   ├── resume_agent.py      # Agent 1 (Sasmitha)
│   │   ├── match_agent.py       # Agent 2 (Isara)
│   │   ├── gap_agent.py         # Agent 3 (Olivea)
│   │   └── decision_agent.py    # Agent 4 (Dinithi)
│   └── tools/
│       ├── file_tools.py        # PDF reader (+ OCR), JD reader, PDF report writer
│       ├── search_tools.py      # DuckDuckGo web search
│       └── reporting_tools.py   # CSV ranking & Matplotlib chart generation
├── tests/
│   ├── llm_evaluator.py         # Shared LLM-as-a-judge helper
│   ├── test_agent_1.py
│   ├── test_agent_2.py
│   ├── test_agent_3.py
│   └── test_agent_4.py
├── local_data/
│   ├── input_resumes/           # Place candidate PDFs here
│   ├── output_reports/          # Individual PDFs, Master CSV, and Chart PNG
│   └── job_description/         # Job Description text files
│       └── jd_software_engineer.txt
├── docs/                        # Technical Report, Agent Docs, Implementation Plan
├── execution_trace.log          # AgentOps observability trace
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
*   **Python 3.10** or higher.
*   **Ollama** installed locally — [Download here](https://ollama.com/download).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull the Local LLM
Ensure Ollama is running, then pull a model. `phi3` is recommended for speed:
```bash
ollama run phi3
```
*Or for higher accuracy:*
```bash
ollama run llama3:8b
```

### 4. Prepare Job Description
Edit or create a plain-text JD file describing the role requirements:
```
local_data/job_description/jd_software_engineer.txt
```

---

## 💻 How to Use It

### Batch Mode (Recommended — Multiple Resumes)
Place all PDF resumes into `local_data/input_resumes/`, then run:
```bash
python -m src.main --folder "local_data/input_resumes" --jd "local_data/job_description/jd_software_engineer.txt"
```

### Single Resume Mode
```bash
python -m src.main --resume "local_data/input_resumes/applicant_1.pdf" --jd "local_data/job_description/jd_software_engineer.txt"
```

### Outputs
After a batch run, check `local_data/output_reports/` for:
*   Individual `<CandidateName>_report.pdf` per resume.
*   `Master_Ranking_Overview.csv` — candidates ranked from highest to lowest match score.
*   `Candidate_Scores_Chart.png` — color-coded bar chart (🟢 ≥70%, 🟡 ≥40%, 🔴 <40%).
*   `execution_trace.log` — full observability trace of every agent and tool call.

---

## 🧪 Testing

We use **pytest** with an **LLM-as-a-Judge** evaluation strategy. A secondary Ollama instance audits each agent's output for hallucinations and structural correctness.

```bash
pytest tests/
```

| Test File | Agent Tested | What It Validates |
| :--- | :--- | :--- |
| `test_agent_1.py` | Resume Parser | No hallucinated skills in extracted profile |
| `test_agent_2.py` | Job Matcher | Match score is valid integer; JSON structure is correct |
| `test_agent_3.py` | Gap Analyzer | Risk level not misclassified; no invented weaknesses |
| `test_agent_4.py` | Decision Agent | PDF created; output contains required headers |



## 🚀 What It Does

*   **Reads Resumes:** Extracts text from a candidate's PDF resume.
*   **Matches Skills:** Checks the candidate's skills against a local database of required job skills.
*   **Finds Gaps:** Identifies missing skills and uses the web to check how important those skills are.
*   **Makes Decisions:** Generates a final PDF report with a "Hire / Reject / Interview" recommendation.
*   **Free and Private:** Runs locally using **Ollama**, meaning candidate data never leaves your computer.

## 👥 Team Contributions

This is a 4-person project. Each member built one agent, one real-world tool, and one automated test.

| Team Member | Role / Agent | Tool Implemented | Testing Focus |
| :--- | :--- | :--- | :--- |
| **Sasmitha** | Resume Parsing Agent | `read_resume_pdf` (PyPDF) | Extraction Accuracy |
| **Isara** | Job Matching Agent | `query_skills_db` (SQLite) | Math & Logic |
| **Olivea** | Gap Analysis Agent | `search_duckduckgo` (Web Search) | AI Hallucination Check |
| **Dinithi** | HR Decision Agent | `generate_pdf_report` (FPDF) | Output Formatting |

## 📂 Repository Structure

```text
project/
├── src/
│   ├── main.py              # LangGraph Orchestrator
│   ├── state/               # TypedDict definitions
│   ├── agents/              # The 4 specialized LLM agents
│   └── tools/               # Real-world interaction tools
├── tests/                   # LLM-as-a-judge test suites
├── local_data/              # Resumes, SQLite DB, Output PDFs
├── scripts/                 # Setup scripts (e.g., DB scaffold)
└── execution_trace.log      # Observability tracking
```

## ⚙️ Setup Instructions

### 1. Prerequisites
*   **Python 3.10** or higher.
*   **Ollama**: Download and install from [ollama.com](https://ollama.com/download).

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the AI Model
Make sure Ollama is running, then download the model we use (Llama 3):
```bash
ollama run llama3:8b
```

### 4. Setup the Database
Run this script to create the local database with job skills:
```bash
python scripts/db_scaffold.py
```

---

## 💻 How to Use It

### Step 1: Add a Resume
Place any PDF resume into the `local_data/input_resumes/` folder. 

> Example: `local_data/input_resumes/applicant_1.pdf`

### Step 2: Run the System
Run the main script and tell it where the resume is and what job you are hiring for. For example:
```bash
python src/main.py --resume "local_data/input_resumes/applicant_1.pdf" --job "Software Engineer"
```

### Step 3: View the Results
*   **The Final Report:** Open `local_data/output_reports/` to see the generated PDF decision.
*   **The Logs:** Open `execution_trace.log` to see exactly what the AI was thinking and doing at each step.

---

## 🧪 Testing Guide

We use **PyTest** to automatically check if our agents are working properly and not making things up (hallucinating). 

Our tests use **LLM-as-a-Judge**, which means we use another AI to double-check the work of our agents.

### How to Run Tests
Make sure Ollama is running in the background, then run:
```bash
pytest tests/
```

### Tests :
*   `test_agent_1.py`: Checks if the Resume Agent correctly extracts the name and skills without making up new ones.
*   `test_agent_2.py`: Checks if the Job Matching Agent can correctly connect to the database and do the math for the match score.
*   `test_agent_3.py`: Checks if the Gap Agent correctly flags missing skills as weaknesses.
*   `test_agent_4.py`: Checks if the Decision Agent properly formats its output with SUMMARY and RECOMMENDATION headers, and successfully creates a PDF.

