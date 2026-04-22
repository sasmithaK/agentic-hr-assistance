import os
import pytest
from langchain_ollama import ChatOllama
from src.agents.resume_agent import ResumeParsingAgent
from src.state.graph_state import AgentState

@pytest.fixture
def mock_state() -> AgentState:
    # Ensure there's a dummy text or pdf we can mock reading.
    # We will simulate a failure or successful parse. 
    # For a unit test, we can mock the `read_resume_pdf` output or use a real small text file.
    # Since we can't guarantee a PDF is there, we'll test the LLM extraction logic directly via process()
    return {
        "input_resume_path": "dummy_path",
        "job_description": "Software Engineer",
        "candidate_profile": {},
        "match_result": {},
        "gap_analysis": {},
        "final_output": ""
    }

# Skip this test if ollama is not running in the CI/CD environment
@pytest.mark.skipif(os.system("curl -s http://localhost:11434/api/tags > /dev/null") != 0, 
                    reason="Requires local Ollama instance running")
def test_resume_agent_extraction_accuracy(monkeypatch, mock_state):
    """
    LLM-as-a-Judge test for Agent 1 (Resume Parsing)
    Validates that the extraction is accurate and doesn't hallucinate.
    """
    # 1. Mock the file reader to return a fixed string
    from src.agents import resume_agent
    dummy_resume = "John Doe is a Python Developer with 4 years of experience using Django, SQL, and Docker."
    monkeypatch.setattr(resume_agent, "read_resume_pdf", lambda x: dummy_resume)

    agent = ResumeParsingAgent()
    result = agent.process(mock_state)
    profile = result.get("candidate_profile", {})
    
    # Assert structural property
    assert "name" in profile
    assert "skills" in profile
    assert isinstance(profile["skills"], list)
    
    # LLM Evaluator
    evaluator_llm = ChatOllama(model="llama3:8b", temperature=0)
    eval_prompt = f"""
    You are an AI Auditor. Evaluate the Resume Parsing Agent's extraction output.
    
    ORIGINAL TEXT:
    {dummy_resume}
    
    AGENT EXTRACTED OUTPUT:
    Name: {profile.get('name')}
    Skills: {', '.join(profile.get('skills', []))}
    Experience: {profile.get('experience_years')}
    
    EVALUATION CRITERIA:
    - Did the agent invent/hallucinate any skill not mentioned in the original text?
    - Is the name correct?
    
    Respond ONLY with 'PASS' if accurate and no hallucinations, or 'FAIL' if errors exist.
    """
    
    eval_response = evaluator_llm.invoke(eval_prompt)
    assert "PASS" in eval_response.content.upper()
