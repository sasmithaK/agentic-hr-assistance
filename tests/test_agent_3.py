import pytest
from src.agents.gap_agent import GapAnalysisAgent
from src.state.graph_state import AgentState

# Mock state for testing
@pytest.fixture
def mock_state_with_gaps() -> AgentState:
    return {
        "input_resume_path": "local_data/input_resumes/test_resume.pdf",
        "job_description": "Software Engineer",
        "candidate_profile": {
            "name": "John Doe",
            "skills": ["Python", "SQL", "Docker"],
            "experience_years": 3,
            "role": "Software Developer"
        },
        "match_result": {
            "match_score": 60,
            "matched_skills": ["Python", "SQL", "Docker"],
            "missing_skills": ["LangChain", "FastAPI"],
            "reasoning": "Candidate has 3 out of 5 required skills"
        },
        "gap_analysis": {},
        "final_output": ""
    }

@pytest.fixture
def mock_state_no_gaps() -> AgentState:
    return {
        "input_resume_path": "local_data/input_resumes/test_resume.pdf",
        "job_description": "Software Engineer",
        "candidate_profile": {
            "name": "Jane Doe",
            "skills": ["Python", "LangChain", "SQL", "Docker", "FastAPI"],
            "experience_years": 5,
            "role": "Software Engineer"
        },
        "match_result": {
            "match_score": 100,
            "matched_skills": ["Python", "LangChain", "SQL", "Docker", "FastAPI"],
            "missing_skills": [],
            "reasoning": "Candidate has all required skills"
        },
        "gap_analysis": {},
        "final_output": ""
    }

def test_gap_analysis_with_missing_skills(mock_state_with_gaps):
    """Test gap analysis when there are missing skills."""
    agent = GapAnalysisAgent()
    result = agent.process(mock_state_with_gaps)
    
    gap_analysis = result.get("gap_analysis", {})
    
    # Basic property assertions
    assert "gap_severity" in gap_analysis
    assert "priority_skills" in gap_analysis
    assert "recommendations" in gap_analysis
    assert "learning_timeline" in gap_analysis
    assert "overall_assessment" in gap_analysis
    assert "learning_resources" in gap_analysis
    
    # Check that missing skills are addressed
    assert isinstance(gap_analysis["priority_skills"], list)
    assert len(gap_analysis["priority_skills"]) > 0
    
    # Check learning resources exist for missing skills
    learning_resources = gap_analysis["learning_resources"]
    missing_skills = mock_state_with_gaps["match_result"]["missing_skills"]
    
    for skill in missing_skills:
        assert skill in learning_resources
        assert isinstance(learning_resources[skill], list)

def test_gap_analysis_no_missing_skills(mock_state_no_gaps):
    """Test gap analysis when there are no missing skills."""
    agent = GapAnalysisAgent()
    result = agent.process(mock_state_no_gaps)
    
    gap_analysis = result.get("gap_analysis", {})
    
    # Should indicate no gaps
    assert gap_analysis.get("status") == "No gaps identified"
    assert gap_analysis.get("recommendations") == []

def test_web_search_tool():
    """Test the web search tool functionality."""
    from src.tools.search_tools import search_web
    
    # Test with a simple query
    results = search_web("learn Python", max_results=2)
    
    # Should return a list
    assert isinstance(results, list)
    
    # If results are found, they should be strings
    if results:
        assert all(isinstance(result, str) for result in results)

def test_agent_node_function():
    """Test that the node function works correctly."""
    from src.agents.gap_agent import gap_analysis_node
    
    mock_state = {
        "job_description": "Software Engineer",
        "match_result": {
            "missing_skills": ["LangChain"]
        },
        "candidate_profile": {"name": "Test User"},
        "gap_analysis": {}
    }
    
    result = gap_analysis_node(mock_state)
    
    assert "gap_analysis" in result
    assert isinstance(result["gap_analysis"], dict)

def test_llm_as_a_judge_hallucination_detection(mock_state_with_gaps):
    """LLM-as-a-Judge test: Validates that the gap analysis agent's output is accurate and free from hallucinations."""
    from tests.llm_evaluator import LLMEvaluator
    
    # Run the gap analysis agent
    agent = GapAnalysisAgent()
    result = agent.process(mock_state_with_gaps)
    
    gap_analysis = result.get("gap_analysis", {})
    missing_skills = mock_state_with_gaps["match_result"]["missing_skills"]
    job_title = mock_state_with_gaps["job_description"]
    
    # Use LLM-as-a-Judge to evaluate the output
    evaluator = LLMEvaluator()
    evaluation = evaluator.evaluate_gap_analysis(gap_analysis, missing_skills, job_title)
    
    # 1. Basic evaluation structure checks
    assert "score" in evaluation
    assert "hallucinations_detected" in evaluation
    assert "issues_found" in evaluation
    assert "strengths" in evaluation
    assert "overall_assessment" in evaluation
    
    # 2. Score should be reasonable (0-100)
    assert isinstance(evaluation["score"], int)
    assert 0 <= evaluation["score"] <= 100
    
    # 3. Hallucination detection should work
    assert isinstance(evaluation["hallucinations_detected"], bool)
    
    # 4. Issues and strengths should be lists
    assert isinstance(evaluation["issues_found"], list)
    assert isinstance(evaluation["strengths"], list)
    
    # 5. No major hallucinations should be detected for basic functionality
    if evaluation["score"] < 50:
        print(f"Low score detected: {evaluation['score']}")
        print(f"Issues: {evaluation['issues_found']}")
        print(f"Assessment: {evaluation['overall_assessment']}")
    
    # 6. The agent should not hallucinate skills that don't exist
    priority_skills = gap_analysis.get("priority_skills", [])
    for skill in priority_skills:
        assert skill in missing_skills, f"Hallucinated skill detected: {skill}"
    
    print(f"LLM-as-a-Judge Evaluation Score: {evaluation['score']}/100")
    print(f"Hallucinations Detected: {evaluation['hallucinations_detected']}")
    print(f"Overall Assessment: {evaluation['overall_assessment']}")

def test_learning_resources_quality_evaluation(mock_state_with_gaps):
    """Test that learning resources found by the agent are relevant and high-quality."""
    from tests.llm_evaluator import LLMEvaluator
    
    # Run the gap analysis agent
    agent = GapAnalysisAgent()
    result = agent.process(mock_state_with_gaps)
    
    gap_analysis = result.get("gap_analysis", {})
    missing_skills = mock_state_with_gaps["match_result"]["missing_skills"]
    learning_resources = gap_analysis.get("learning_resources", {})
    
    # Use LLM-as-a-Judge to evaluate learning resources
    evaluator = LLMEvaluator()
    resource_evaluation = evaluator.evaluate_learning_resources(learning_resources, missing_skills)
    
    # 1. Basic evaluation structure checks
    assert "coverage_score" in resource_evaluation
    assert "relevance_score" in resource_evaluation
    assert "quality_issues" in resource_evaluation
    assert "missing_resources" in resource_evaluation
    assert "overall_quality" in resource_evaluation
    
    # 2. Scores should be reasonable (0-100)
    assert isinstance(resource_evaluation["coverage_score"], int)
    assert isinstance(resource_evaluation["relevance_score"], int)
    assert 0 <= resource_evaluation["coverage_score"] <= 100
    assert 0 <= resource_evaluation["relevance_score"] <= 100
    
    # 3. Coverage should be decent for basic skills
    assert resource_evaluation["coverage_score"] >= 30, "Poor coverage of learning resources"
    
    print(f"Learning Resources Coverage Score: {resource_evaluation['coverage_score']}/100")
    print(f"Learning Resources Relevance Score: {resource_evaluation['relevance_score']}/100")
    print(f"Overall Quality: {resource_evaluation['overall_quality']}")

if __name__ == "__main__":
    # For manual verification
    pytest.main([__file__])
