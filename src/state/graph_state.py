from typing import TypedDict, Dict, Any, List

class AgentState(TypedDict):
    """
    Global state for the HR Candidate Screening Support Assistant.
    Ensures structured context is passed between agents in the LangGraph pipeline.
    """
    input_resume_path: str
    job_description: str
    candidate_profile: Dict[str, Any]
    match_result: Dict[str, Any]  # Should contain 'match_score': int/float
    gap_analysis: Dict[str, Any]
    final_output: str

class BatchState(TypedDict):
    """
    State representing the aggregation of all processed candidates in a batch.
    """
    candidates: List[AgentState]
    master_report_path: str
    graph_path: str
