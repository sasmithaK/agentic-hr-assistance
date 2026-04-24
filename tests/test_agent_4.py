import os
import pytest
from src.state.graph_state import AgentState
from src.tools.file_tools import generate_pdf_report
from src.agents.decision_agent import hr_decision_node

def test_generate_pdf_report_success():
    """
    Automated Evaluation (Component Check): 
    Validates that the specific custom Python tool generates the targeted PDF 
    and saves to the right location without throwing errors.
    """
    mock_state: AgentState = {
        "input_resume_path": "",
        "job_description": "Software Engineer",
        "candidate_profile": {"name": "Test Candidate"},
        "match_result": {"match_score": 95},
        "gap_analysis": {"weaknesses": ["Kubernetes"]},
        "final_output": "SUMMARY: Good candidate.\nRECOMMENDATION: Interview."
    }
    
    # Run tool
    filepath = generate_pdf_report(mock_state)
    
    # Asserts
    assert "Error:" not in filepath
    assert os.path.exists(filepath), f"Tool failed to write PDF to path: {filepath}"
    assert filepath.endswith(".pdf")
    
    # Cleanup post-test
    if os.path.exists(filepath):
         os.remove(filepath)

@pytest.mark.ollama
def test_decision_agent_formatting_and_constraints():
    """
    Automated Evaluation (Property-Based / Output format assertion):
    Validates that the specific Agent correctly respects the system prompt 
    formatting constraints without hallucinating.
    """
    mock_state: AgentState = {
        "input_resume_path": "",
        "job_description": "Data Scientist",
        "candidate_profile": {"name": "John Doe", "skills": ["SQL", "Python", "Pandas"]},
        "match_result": {"match_score": 70},
        "gap_analysis": {"weaknesses": ["Spark"]},
        "final_output": ""
    }
    
    # Run Agent
    new_state = hr_decision_node(mock_state)
    decision = new_state.get("final_output", "")
    
    # Enforce formatting constraints designed in the prompt
    assert "SUMMARY" in decision.upper(), "Agent hallucinated/failed to include SUMMARY section"
    assert "RECOMMENDATION" in decision.upper(), "Agent hallucinated/failed to include RECOMMENDATION section"
    
    # Enforce no fallback error
    assert "CRITICAL SYSTEM ERROR" not in decision

