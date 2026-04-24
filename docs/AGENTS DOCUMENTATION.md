# HR Candidate Screening Support Assistant - Agent Documentation

This document provides comprehensive details regarding the four distinct AI agents operating within the LangGraph orchestrator. It outlines their roles, tool integration, state requirements, testing strategies, and critical considerations for maintaining system stability.

---

## Agent 1: Resume Parsing Agent
**Designed by:** Sasmitha

### 1. Overview
*   **Role:** Extract structured data from raw, unstructured candidate resumes.
*   **Persona:** HR Data Extraction Specialist.
*   **Core Responsibility:** Convert large blocks of PDF text into a clean, strictly-typed JSON profile containing the candidate's name, skills, experience years, and current role.

### 2. Tool Integration
*   **Tool Name:** `read_resume_pdf(filepath: str) -> str`
*   **Functionality:** Interacts with the local file system using the `pypdf` library to extract raw text from PDF documents. If the standard extraction returns 0 characters (image-based PDF), it automatically falls back to `pytesseract` + `pdf2image` for OCR-based extraction.

### 3. State Management
*   **Inputs Consumed:** `input_resume_path` (str)
*   **Outputs Produced:** `candidate_profile` (Dict)
    *   *Example Output:* `{"name": "Jane Doe", "skills": ["Python", "Docker"], "experience_years": 5, "role": "Software Engineer"}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** *Zero Hallucination.* The agent is explicitly instructed to extract *only* the skills mentioned in the text and never infer or invent abilities.
*   **Formatting Requirement:** Must output pure JSON with keys: `name`, `skills`, `experience_years`, `role`.

### 5. Testing Strategy
*   **Approach:** LLM-as-a-Judge (`test_agent_1.py`).
*   **Evaluation:** A secondary LLM is fed the original raw text and the agent's extracted JSON, checking specifically if the agent invented any skills not present in the original text.

### 6. Things to Keep in Mind
*   **Context Window Limits:** The tool truncates resume text to the first 3,000 characters to avoid LLM token overflow.
*   **OCR Fallback:** If the PDF is scanned/image-based, `pytesseract` is invoked automatically. This requires the Tesseract engine to be installed on the host machine.

---

## Agent 2: Job Matching Agent
**Designed by:** Isara

### 1. Overview
*   **Role:** Semantically compare the candidate profile against the full Job Description to quantify fit.
*   **Persona:** Precision-oriented HR Data Analyst.
*   **Core Responsibility:** Identify matched skills, missing skills, and calculate a quantitative match score (0-100 integer).

### 2. Tool Integration
*   **Tool Name:** `read_job_description(filepath: str) -> str`
*   **Functionality:** Reads a plain-text or Markdown Job Description file from the local file system (`local_data/jd_*.txt`) and returns its full text content for semantic analysis by the LLM. This replaces rigid database keyword matching with flexible, context-aware reasoning.

### 3. State Management
*   **Inputs Consumed:** `job_description` (str â€” file path), `candidate_profile` (Dict)
*   **Outputs Produced:** `match_result` (Dict)
    *   *Example Output:* `{"match_score": 75, "matched_skills": ["Python", "Docker"], "missing_skills": ["AWS"], "reasoning": "Strong backend skills but lacks cloud experience."}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** Must return `match_score` as a strict integer (0-100). The JSON parser enforces `int()` casting to prevent floats or strings from breaking downstream tools.
*   **Formatting Requirement:** Must output pure JSON with keys: `match_score`, `matched_skills`, `missing_skills`, `reasoning`.

### 5. Testing Strategy
*   **Approach:** Property-Based + LLM-as-a-Judge (`test_agent_2.py`).
*   **Evaluation:** Validates the `match_score` is an integer between 0 and 100, and uses an AI Auditor to confirm the mathematical reasoning aligns with the given inputs.

### 6. Things to Keep in Mind
*   **JD File Not Found:** If the JD file path is invalid, the tool returns an `Error:` prefixed string. The agent detects this and returns a zero-score fallback instead of crashing.
*   **Semantic Matching:** The LLM is responsible for recognizing that "ReactJS" in the resume semantically matches "React" in the JD.

---

## Agent 3: Gap Analysis Agent
**Designed by:** Olivea

### 1. Overview
*   **Role:** Assess the severity of missing skills and check for context on unfamiliar terms.
*   **Persona:** HR Technical Assessor.
*   **Core Responsibility:** Classify the risk level of hiring the candidate based on what they are missing, leveraging real-world web context for obscure technical terms.

### 2. Tool Integration
*   **Tool Name:** `search_duckduckgo(query: str) -> List[Dict[str, Any]]`
*   **Functionality:** Interacts with the free `duckduckgo-search` public API to look up how critical a missing skill is for the target role. If DuckDuckGo rate-limits the request (returns 0 results), the tool gracefully returns an empty list and the agent falls back to its inherent knowledge.

### 3. State Management
*   **Inputs Consumed:** `job_description` (str), `match_result` (Dict)
*   **Outputs Produced:** `gap_analysis` (Dict)
    *   *Example Output:* `{"strengths": ["Python", "FastAPI"], "weaknesses": ["AWS", "Kubernetes"], "risk_level": "Medium", "analysis_summary": "Solid core skills but lacks cloud infrastructure experience."}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** Must not contradict the Matching Agent. It must only analyze the `missing_skills` provided by Agent 2 in the state.
*   **Formatting Requirement:** Must output pure JSON with keys: `strengths`, `weaknesses`, `risk_level` (Low/Medium/High), `analysis_summary`.

### 5. Testing Strategy
*   **Approach:** LLM-as-a-Judge (`test_agent_3.py`).
*   **Evaluation:** Verifies that the agent did not hallucinate new weaknesses that were not explicitly passed from the Match Agent's state.

### 6. Things to Keep in Mind
*   **API Rate Limiting:** Free web search APIs can rate-limit under heavy batch load. The tool limits queries to 3 results max and catches timeout/HTTP exceptions gracefully.
*   **Risk Logic:** The agent uses inherent LLM knowledge + web context snippets to determine if a missing skill is "High" risk (e.g., missing Python for a Python Developer role) or "Low" risk (e.g., missing a specific agile tracking tool).

---

## Agent 4: HR Decision Agent
**Designed by:** Dinithi

### 1. Overview
*   **Role:** Synthesize all previous node data into a final, readable HR recommendation, and generate batch-level reporting outputs.
*   **Persona:** Elite, Evidence-based Senior HR Executive.
*   **Core Responsibility:** Make the final Hire/Interview/Reject decision, write the justification, and â€” in batch mode â€” produce a ranked CSV and a data visualization chart comparing all candidates.

### 2. Tool Integration
*   **Tool Name 1:** `generate_pdf_report(state: AgentState) -> str`
    *   **Functionality:** Uses the `FPDF` library to generate a formatted per-candidate PDF report saved to `local_data/output_reports/`.
*   **Tool Name 2:** `generate_ranked_csv(candidates: List[Dict]) -> str`
    *   **Functionality:** Uses `pandas` to aggregate all processed candidates, sort them by `match_score` (highest to lowest), and save a `Master_Ranking_Overview.csv`.
*   **Tool Name 3:** `generate_score_graphs(candidates: List[Dict]) -> str`
    *   **Functionality:** Uses `matplotlib` to produce a color-coded bar chart (`Candidate_Scores_Chart.png`) comparing all candidates' match scores. Green â‰¥70%, Amber â‰¥40%, Red <40%.

### 3. State Management
*   **Inputs Consumed:** `candidate_profile` (Dict), `job_description` (str), `match_result` (Dict), `gap_analysis` (Dict)
*   **Outputs Produced:** `final_output` (str)

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** *Synthesize Only.* Absolutely zero hallucination permitted. The decision must be based entirely on the provided state matrices.
*   **Formatting Requirement:** Must output text strictly formatted with three headers: `SUMMARY`, `JUSTIFICATION`, and `RECOMMENDATION`.

### 5. Testing Strategy
*   **Approach:** Component & Output Formatting Assertion (`test_agent_4.py`).
*   **Evaluation:** Asserts that the PDF is successfully written to the correct path, and verifies the LLM output contains the required markdown headers.

### 6. Things to Keep in Mind
*   **String Sanitization for PDFs:** The FPDF library uses `latin-1` encoding. The tool explicitly sanitizes the LLM's output (encoding with `replace` error handling) before writing to prevent `UnicodeEncodeError`.
*   **Batch vs. Single Mode:** The CSV and chart tools are only triggered by the orchestrator (`main.py`) after the full batch loop completes, not after individual resume processing.

