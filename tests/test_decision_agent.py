import os
import pytest
from src.state.graph_state import GraphState
from src.tools.file_tools import generate_pdf_report
from src.agents.decision_agent import hr_decision_node

def test_generate_pdf_report_success():
    """
    Automated Evaluation (Component Check): 
    Validates that the specific custom Python tool generates the targeted PDF 
    and saves to the right location without throwing errors.
    """
    mock_state: GraphState = {
        "applicant_name": "Test Candidate",
        "target_job": "Software Engineer",
        "parsed_resume_text": "Knows Python tightly.",
        "job_matching_matrix": "Match: 95%",
        "gap_analysis_report": "Missing: Kubernetes",
        "final_decision": "SUMMARY: Good candidate.\nRECOMMENDATION: Interview."
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

# Skip this test if ollama is not running in the CI/CD environment
@pytest.mark.skipif(os.system("curl -s http://localhost:11434/api/tags > /dev/null") != 0, 
                    reason="Requires local Ollama instance running")
def test_decision_agent_formatting_and_constraints():
    """
    Automated Evaluation (Property-Based / Output format assertion):
    Validates that the specific Agent correctly respects the system prompt 
    formatting constraints without hallucinating.
    """
    mock_state: GraphState = {
        "applicant_name": "John Doe",
        "target_job": "Data Scientist",
        "parsed_resume_text": "SQL, Python, Pandas.",
        "job_matching_matrix": "Match 70%",
        "gap_analysis_report": "Lacks Spark.",
        "final_decision": None
    }
    
    # Run Agent
    new_state = hr_decision_node(mock_state)
    decision = new_state.get("final_decision", "")
    
    # Enforce formatting constraints designed in the prompt
    assert "SUMMARY" in decision.upper(), "Agent hallucinated/failed to include SUMMARY section"
    assert "RECOMMENDATION" in decision.upper(), "Agent hallucinated/failed to include RECOMMENDATION section"
    
    # Enforce no fallback error
    assert "CRITICAL SYSTEM ERROR" not in decision
