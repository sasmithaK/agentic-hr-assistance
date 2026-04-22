import os
import pytest
from langchain_ollama import ChatOllama
from src.agents.gap_agent import GapAnalysisAgent
from src.state.graph_state import AgentState

@pytest.fixture
def mock_state() -> AgentState:
    return {
        "input_resume_path": "",
        "job_description": "DevOps Engineer",
        "candidate_profile": {
            "name": "Alex",
            "skills": ["Linux", "Python"]
        },
        "match_result": {
            "match_score": 40,
            "matched_skills": ["Linux", "Python"],
            "missing_skills": ["Kubernetes", "AWS", "Terraform"]
        },
        "gap_analysis": {},
        "final_output": ""
    }

@pytest.mark.skipif(os.system("curl -s http://localhost:11434/api/tags > /dev/null") != 0, 
                    reason="Requires local Ollama instance running")
def test_gap_agent_accuracy(mock_state):
    """
    LLM-as-a-Judge test for Agent 3 (Gap Analysis)
    Validates that the gap analysis accurately processes strengths and weaknesses without hallucinating.
    """
    agent = GapAnalysisAgent()
    result = agent.process(mock_state)
    gap_analysis = result.get("gap_analysis", {})
    
    # Assert structural property
    assert "strengths" in gap_analysis
    assert "weaknesses" in gap_analysis
    assert "risk_level" in gap_analysis
    
    evaluator_llm = ChatOllama(model="llama3:8b", temperature=0)
    
    eval_prompt = f"""
    You are an AI Auditor. Evaluate the Gap Analysis Agent's output.
    
    MISSING SKILLS (Truth): Kubernetes, AWS, Terraform
    
    AGENT OUTPUT:
    Weaknesses: {', '.join(gap_analysis.get('weaknesses', []))}
    Risk Level: {gap_analysis.get('risk_level')}
    Summary: {gap_analysis.get('analysis_summary')}
    
    EVALUATION CRITERIA:
    - Did the agent hallucinate any weakness that was NOT in the 'MISSING SKILLS (Truth)' list?
    - Is the Risk Level reasonable for someone missing 3 core skills (should be Medium or High)?
    
    Respond ONLY with 'PASS' if accurate and no hallucinations, or 'FAIL' if errors exist.
    """
    
    eval_response = evaluator_llm.invoke(eval_prompt)
    assert "PASS" in eval_response.content.upper()
