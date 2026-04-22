# HR Candidate Screening Support Assistant - Agent Documentation

This document provides comprehensive details regarding the four distinct AI agents operating within the LangGraph orchestrator. It outlines their roles, tool integration, state requirements, testing strategies, and critical considerations for maintaining system stability.

---

## Agent 1: Resume Parsing Agent
**Designed by:** Student 1

### 1. Overview
*   **Role:** Extract structured data from raw, unstructured candidate resumes.
*   **Persona:** HR Data Extraction Specialist.
*   **Core Responsibility:** Convert large blocks of PDF text into a clean, strictly-typed JSON profile containing the candidate's name, skills, experience, and role.

### 2. Tool Integration
*   **Tool Name:** `read_resume_pdf(filepath: str) -> str`
*   **Functionality:** Interacts with the local file system using the `pypdf` library to extract raw strings from PDF documents without relying on external OCR APIs.

### 3. State Management
*   **Inputs Consumed:** `input_resume_path` (str)
*   **Outputs Produced:** `candidate_profile` (Dict)
    *   *Example Output:* `{"name": "Jane Doe", "skills": ["Python", "Docker"], "experience_years": 5, "role": "Software Engineer"}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** *Zero Hallucination.* The agent is explicitly instructed to extract *only* the skills mentioned in the text and never infer or invent abilities based on the job title.
*   **Formatting Requirement:** Must output pure JSON.

### 5. Testing Strategy
*   **Approach:** LLM-as-a-Judge (`test_agent_1.py`).
*   **Evaluation:** A secondary LLM is fed the original raw text and the agent's extracted JSON, checking specifically if the agent invented any skills not present in the original text.

### 6. Things to Keep in Mind
*   **Context Window Limits:** Resumes can be long. Ensure the tool truncates the text to fit within the `llama3:8b` context window (e.g., capping at 3,000-4,000 characters) to avoid token limits or memory crashes.
*   **Parsing Errors:** If the PDF is an image or corrupted, the tool will return an error string. The agent must gracefully handle this, and the orchestrator should short-circuit the pipeline to avoid wasting tokens on downstream agents.

---

## Agent 2: Job Matching Agent
**Designed by:** Student 2

### 1. Overview
*   **Role:** Compare candidate skills against the mandatory skills required for the job.
*   **Persona:** Precision-oriented HR Data Analyst.
*   **Core Responsibility:** Identify matched skills, missing skills, and calculate a quantitative match score (0-100%).

### 2. Tool Integration
*   **Tool Name:** `query_skills_db(job_title: str) -> List[str]`
*   **Functionality:** Executes a SQL `SELECT` statement against `local_data/hr_database.db` to retrieve the baseline skillset required for the target job title.

### 3. State Management
*   **Inputs Consumed:** `job_description` (str), `candidate_profile` (Dict)
*   **Outputs Produced:** `match_result` (Dict)
    *   *Example Output:* `{"match_score": 75, "matched_skills": ["Python"], "missing_skills": ["AWS"], "reasoning": "Missing cloud experience."}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** Must perform exact or semantic matching between the candidate's skills and the database requirements.
*   **Formatting Requirement:** Must output pure JSON.

### 5. Testing Strategy
*   **Approach:** Property-Based + LLM-as-a-Judge (`test_agent_2.py`).
*   **Evaluation:** Validates the structural integrity of the score integer, and utilizes an AI Auditor to confirm the mathematical reasoning aligns with the given inputs.

### 6. Things to Keep in Mind
*   **Database Sync:** If a user inputs a job title that does not exist in the database, the tool will return an empty list. The agent must be programmed to handle empty reference lists without crashing.
*   **Semantic Matching:** The LLM is responsible for recognizing that "ReactJS" in the resume matches "React" in the database.

---

## Agent 3: Gap Analysis Agent
**Designed by:** Student 3

### 1. Overview
*   **Role:** Assess the severity of missing skills and check for context on unfamiliar terms.
*   **Persona:** HR Technical Assessor.
*   **Core Responsibility:** Classify the risk level of hiring the candidate based on what they are missing, leveraging real-world context for obscure technical terms.

### 2. Tool Integration
*   **Tool Name:** `search_duckduckgo(query: str) -> List[Dict[str, Any]]`
*   **Functionality:** Interacts with a free public API (`duckduckgo-search`) to search the web and pull context regarding how critical a missing skill is for the target role.

### 3. State Management
*   **Inputs Consumed:** `job_description` (str), `match_result` (Dict)
*   **Outputs Produced:** `gap_analysis` (Dict)
    *   *Example Output:* `{"strengths": ["Python"], "weaknesses": ["AWS"], "risk_level": "Medium", "analysis_summary": "Solid core skills but lacks cloud infrastructure."}`

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** Must not contradict the Matching Agent. It must only analyze the `missing_skills` provided in the state.
*   **Formatting Requirement:** Must output pure JSON.

### 5. Testing Strategy
*   **Approach:** LLM-as-a-Judge (`test_agent_3.py`).
*   **Evaluation:** Verifies that the agent did not hallucinate new weaknesses that were not explicitly passed from the Match Agent's state.

### 6. Things to Keep in Mind
*   **API Rate Limiting:** Free web search APIs can rate-limit you if you send too many requests. The tool should limit queries to 1-3 results max and handle HTTP timeout exceptions gracefully.
*   **Risk Logic:** The agent relies on its inherent knowledge + web context to determine if a missing skill is a "High" risk (e.g., missing Python for a Python Developer) or "Low" risk (missing a specific agile tracking tool).

---

## Agent 4: HR Decision Agent
**Designed by:** Student 4

### 1. Overview
*   **Role:** Synthesize all previous node data into a final, readable HR recommendation.
*   **Persona:** Elite, Evidence-based Senior HR Executive.
*   **Core Responsibility:** Make the final Hire/Interview/Reject decision and write the justification.

### 2. Tool Integration
*   **Tool Name:** `generate_pdf_report(state: AgentState) -> str`
*   **Functionality:** Interacts with the local file system using the `FPDF` library to generate a formatted PDF report securely saved to the `output_reports` directory.

### 3. State Management
*   **Inputs Consumed:** `candidate_profile` (Dict), `job_description` (str), `match_result` (Dict), `gap_analysis` (Dict)
*   **Outputs Produced:** `final_output` (str)

### 4. Constraints & Prompt Engineering
*   **Critical Constraint:** *Synthesize Only.* Absolutely zero hallucination is permitted. The decision must be based entirely on the provided state matrices.
*   **Formatting Requirement:** Must output text strictly formatted with three headers: `SUMMARY`, `JUSTIFICATION`, and `RECOMMENDATION`.

### 5. Testing Strategy
*   **Approach:** Component & Output Formatting Assertion (`test_agent_4.py`).
*   **Evaluation:** Asserts that the tool successfully writes the PDF to the correct path, and verifies that the LLM adhered strictly to the requested markdown headers without falling back to generic conversational text.

### 6. Things to Keep in Mind
*   **String Formatting for PDFs:** The LLM's final output can contain unicode characters, emojis, or markdown that `FPDF` cannot handle natively using standard `latin-1` encoding. The tool must sanitize or encode the text safely before writing to PDF to prevent `UnicodeEncodeError`.
*   **No JSON:** This is the only agent that does *not* output JSON, making it easier to parse via LangGraph's standard text output mechanisms.
