from typing import TypedDict, Optional

class GraphState(TypedDict):
    """
    Represents the global state of the Multi-Agent HR Candidate Screening System.
    Strictly utilized by LangGraph to pass context between agents seamlessly.
    """
    applicant_name: str
    target_job: str
    parsed_resume_text: str
    job_matching_matrix: str
    gap_analysis_report: str
    final_decision: Optional[str]
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
