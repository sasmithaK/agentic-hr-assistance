import os
import pytest
from langchain_ollama import ChatOllama
from src.agents.match_agent import JobMatchingAgent
from src.state.graph_state import AgentState

JD_PATH = "local_data/job_description/jd_software_engineer.txt"

@pytest.fixture
def mock_state() -> AgentState:
    return {
        "input_resume_path": "local_data/input_resumes/test_resume.pdf",
        "job_description": JD_PATH,
        "candidate_profile": {
            "name": "Jane Doe",
            "skills": ["Python", "Docker", "Git", "FastAPI", "PostgreSQL"],
            "experience_years": 4,
            "education": "BSc Computer Science",
            "role": "Software Developer"
        },
        "match_result": {},
        "gap_analysis": {},
        "final_output": ""
    }

@pytest.mark.skipif(
    not os.path.exists(JD_PATH),
    reason="JD file not found at local_data/job_description/jd_software_engineer.txt"
)
def test_jd_file_readable():
    """Property-based test: Ensure the JD file tool can read the job description."""
    from src.tools.file_tools import read_job_description
    content = read_job_description(JD_PATH)
    assert not content.startswith("Error:"), f"JD read failed: {content}"
    assert len(content) > 50, "JD file appears to be empty or too short"
    assert "Python" in content, "JD should mention Python as a required skill"

@pytest.mark.skipif(
    os.system("curl -s http://localhost:11434/api/tags > /dev/null") != 0,
    reason="Requires local Ollama instance running"
)
def test_agent_matching_logic(mock_state):
    """LLM-as-a-Judge test: Validates that the match agent output is logical and accurate."""
    agent = JobMatchingAgent()
    result = agent.process(mock_state)

    match_result = result.get("match_result", {})

    # 1. Structural property assertions
    assert "match_score" in match_result, "match_result missing 'match_score' key"
    assert "matched_skills" in match_result, "match_result missing 'matched_skills' key"
    assert "missing_skills" in match_result, "match_result missing 'missing_skills' key"
    assert isinstance(match_result["match_score"], int), "match_score must be an integer"
    assert 0 <= match_result["match_score"] <= 100, "match_score must be between 0 and 100"

    # 2. LLM-as-a-Judge Evaluation
    evaluator_llm = ChatOllama(model="llama3:8b", temperature=0)

    eval_prompt = f"""
    You are an AI Auditor. Evaluate the following Job Matching Agent's output for accuracy and honesty.
    
    JOB DESCRIPTION: The candidate is being matched against a Software Engineer role requiring Python, FastAPI, PostgreSQL, Docker, and Git.
    CANDIDATE SKILLS: Python, Docker, Git, FastAPI, PostgreSQL (4 years experience)
    
    AGENT OUTPUT:
    Score: {match_result.get('match_score')}%
    Matched Skills: {', '.join(match_result.get('matched_skills', []))}
    Missing Skills: {', '.join(match_result.get('missing_skills', []))}
    Reasoning: {match_result.get('reasoning')}
    
    EVALUATION CRITERIA:
    - Did the agent hallucinate any skills not found in both the JD and Candidate lists?
    - Is the match score reasonable? (Candidate has all 5 core skills, so score should be HIGH, above 70%)
    
    Respond ONLY with 'PASS' if the output is accurate and follows the criteria, or 'FAIL' if there are errors or hallucinations.
    """

    eval_response = evaluator_llm.invoke(eval_prompt)
    assert "PASS" in eval_response.content.upper(), f"LLM Judge returned FAIL: {eval_response.content}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
