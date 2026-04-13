import pytest
import sqlite3
import os
from langchain_ollama import ChatOllama
from src.agents.match_agent import JobMatchingAgent
from src.state.graph_state import AgentState

# Mock state for testing
@pytest.fixture
def mock_state() -> AgentState:
    return {
        "input_resume_path": "local_data/input_resumes/test_resume.pdf",
        "job_description": "Software Engineer",
        "candidate_profile": {
            "name": "Jane Doe",
            "skills": ["Python", "SQL", "Docker", "Git", "Java"],
            "experience_years": 5,
            "role": "Software Developer"
        },
        "match_result": {},
        "gap_analysis": {},
        "final_output": ""
    }

def test_database_retrieval():
    """Property-based test: Ensure the DB tool retrieves expected data."""
    from src.tools.database_tools import query_skills_db
    
    skills = query_skills_db("Software Engineer")
    assert isinstance(skills, list)
    assert len(skills) > 0
    assert "Python" in skills

def test_agent_matching_logic(mock_state):
    """LLM-as-a-Judge test: Validates that the agent's output is logical and accurate."""
    agent = JobMatchingAgent()
    result = agent.process(mock_state)
    
    match_result = result.get("match_result", {})
    
    # 1. Basic property assertions
    assert "match_score" in match_result
    assert "matched_skills" in match_result
    assert isinstance(match_result["match_score"], int)
    
    # 2. LLM-as-a-Judge Evaluation
    # We use a secondary LLM call to judge the agent's work
    evaluator_llm = ChatOllama(model="llama3:8b", temperature=0)
    
    # Required skills from DB for "Software Engineer" are: "Python, LangChain, SQL, Docker, FastAPI"
    # Candidate skills: ["Python", "SQL", "Docker", "Git", "Java"]
    # Expected matches: Python, SQL, Docker
    
    eval_prompt = f"""
    You are an AI Auditor. Evaluate the following Job Matching Agent's output for accuracy and honesty.
    
    JOB: Software Engineer
    REQUIRED SKILLS: Python, LangChain, SQL, Docker, FastAPI
    CANDIDATE SKILLS: Python, SQL, Docker, Git, Java
    
    AGENT OUTPUT:
    Score: {match_result.get('match_score')}%
    Matched Skills: {', '.join(match_result.get('matched_skills', []))}
    Reasoning: {match_result.get('reasoning')}
    
    EVALUATION CRITERIA:
    - Did the agent hallucinate any skills not found in both Required and Candidate lists?
    - Is the match score reasonable (3 matches out of 5 required skills ~ 60%)?
    
    Respond ONLY with 'PASS' if the output is accurate and follows the criteria, or 'FAIL' if there are errors or hallucinations.
    """
    
    eval_response = evaluator_llm.invoke(eval_prompt)
    assert "PASS" in eval_response.content.upper()

if __name__ == "__main__":
    # For manual verification
    pytest.main([__file__])
