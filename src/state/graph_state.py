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
