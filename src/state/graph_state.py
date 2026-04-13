from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Global state for the HR Candidate Screening Support Assistant.
    Ensures structured context is passed between agents in the LangGraph pipeline.
    """
    input_resume_path: str
    job_description: str
    candidate_profile: Dict[str, Any]
    match_result: Dict[str, Any]
    gap_analysis: Dict[str, Any]
    final_output: str
