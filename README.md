# HR Candidate Screening Support Assistant 🤖📁

![Agentic AI Architecture](https://img.shields.io/badge/Architecture-LangGraph-blue)
![LLM Setup](https://img.shields.io/badge/LLM-Local_Ollama-green)

A local, AI-powered system that automates the HR candidate screening process. It uses four specialized AI "agents" that work together to read resumes, match skills to a job description, find skill gaps, and make a final hiring decision.


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

## ⚙️ Setup Instructions

### 1. Prerequisites
*   **Python 3.10** or higher.
*   **Ollama**: Download and install from [ollama.com](https://ollama.com/download).

### 2. Install Dependancies

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

