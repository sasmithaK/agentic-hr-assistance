import argparse
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.state.graph_state import AgentState
from src.agents.match_agent import job_matching_node
from src.agents.gap_agent import gap_analysis_node
from src.utils.logger import logger

def create_workflow() -> StateGraph:
    """
    Creates and returns the LangGraph workflow for HR candidate screening.
    
    The workflow processes candidate resumes through multiple agents:
    1. Job Matching Agent - Compares skills with job requirements
    2. Gap Analysis Agent - Identifies missing skills and learning resources
    
    Returns:
        StateGraph: Configured workflow graph
    """
    # Create the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents) to the workflow
    workflow.add_node("job_matching", job_matching_node)
    workflow.add_node("gap_analysis", gap_analysis_node)
    
    # Define the entry point
    workflow.set_entry_point("job_matching")
    
    # Add conditional edges for workflow routing
    def should_continue_gap_analysis(state: AgentState) -> str:
        """
        Determines if gap analysis should continue based on match results.
        
        Args:
            state: Current workflow state
            
        Returns:
            str: Next node name or "END" to terminate
        """
        match_result = state.get("match_result", {})
        
        # If there was an error in matching, end the workflow
        if "error" in match_result:
            logger.warning("Error in job matching, ending workflow")
            return "END"
        
        # If no missing skills, skip gap analysis
        missing_skills = match_result.get("missing_skills", [])
        if not missing_skills:
            logger.info("No missing skills found, skipping gap analysis")
            return "END"
        
        # Continue to gap analysis
        return "gap_analysis"
    
    # Add edges
    workflow.add_conditional_edges(
        "job_matching",
        should_continue_gap_analysis,
        {
            "gap_analysis": "gap_analysis",
            "END": END
        }
    )
    
    # Gap analysis always ends the workflow
    workflow.add_edge("gap_analysis", END)
    
    return workflow

def run_screening(resume_path: str, job_title: str) -> Dict[str, Any]:
    """
    Runs the complete HR screening workflow.
    
    Args:
        resume_path: Path to the candidate's resume file
        job_title: Title of the job to screen for
        
    Returns:
        Dict[str, Any]: Final workflow state with all agent results
    """
    logger.info(f"Starting HR screening for job: {job_title}")
    logger.info(f"Resume file: {resume_path}")
    
    # Create initial state
    initial_state = AgentState(
        input_resume_path=resume_path,
        job_description=job_title,
        candidate_profile={},  # Will be filled by resume parsing agent (not implemented yet)
        match_result={},
        gap_analysis={},
        final_output=""
    )
    
    # Create and run workflow
    workflow = create_workflow()
    
    try:
        # Compile and run the workflow
        app = workflow.compile()
        result = app.invoke(initial_state)
        
        logger.info("HR screening workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        return {"error": str(e)}

def main():
    """Main function to run the HR screening system from command line."""
    parser = argparse.ArgumentParser(description="HR Candidate Screening Support Assistant")
    parser.add_argument(
        "--resume", 
        required=True, 
        help="Path to the candidate's resume PDF file"
    )
    parser.add_argument(
        "--job", 
        required=True, 
        help="Job title to screen the candidate for"
    )
    
    args = parser.parse_args()
    
    # Run the screening process
    result = run_screening(args.resume, args.job)
    
    # Print results summary
    print("\n" + "="*50)
    print("HR SCREENING RESULTS")
    print("="*50)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        # Job matching results
        match_result = result.get("match_result", {})
        if match_result:
            print(f"📊 Match Score: {match_result.get('match_score', 'N/A')}%")
            print(f"✅ Matched Skills: {', '.join(match_result.get('matched_skills', []))}")
            print(f"❌ Missing Skills: {', '.join(match_result.get('missing_skills', []))}")
        
        # Gap analysis results
        gap_analysis = result.get("gap_analysis", {})
        if gap_analysis and gap_analysis.get("status") != "No gaps identified":
            print(f"\n🎯 Gap Severity: {gap_analysis.get('gap_severity', 'N/A')}")
            print(f"📚 Priority Skills: {', '.join(gap_analysis.get('priority_skills', []))}")
            print(f"⏰ Learning Timeline: {gap_analysis.get('learning_timeline', 'N/A')}")
            print(f"📝 Assessment: {gap_analysis.get('overall_assessment', 'N/A')}")
        elif gap_analysis.get("status") == "No gaps identified":
            print("\n🎉 No skill gaps identified!")
    
    print("="*50)

if __name__ == "__main__":
    main()
