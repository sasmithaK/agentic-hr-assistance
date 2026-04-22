import argparse
import os
from langgraph.graph import StateGraph, END
from src.state.graph_state import AgentState
from src.agents.resume_agent import resume_parsing_node
from src.agents.match_agent import job_matching_node
from src.agents.gap_agent import gap_analysis_node
from src.agents.decision_agent import hr_decision_node
from src.tools.file_tools import generate_pdf_report
from src.utils.logger import get_agent_logger

logger = get_agent_logger("Orchestrator")

def should_continue(state: AgentState):
    """
    Conditional edge function. If the resume parsing fails, short-circuit to END.
    """
    if "error" in state.get("candidate_profile", {}):
        logger.warning("Short-circuiting workflow due to parsing error.")
        return END
    return "match_node"

def build_graph():
    """
    Builds the LangGraph StateGraph mapping the HR candidate screening workflow.
    """
    # 1. Initialize StateGraph with our strict TypedDict
    workflow = StateGraph(AgentState)
    
    # 2. Add specific nodes mapped to our Agents
    workflow.add_node("resume_node", resume_parsing_node)
    workflow.add_node("match_node", job_matching_node)
    workflow.add_node("gap_node", gap_analysis_node)
    workflow.add_node("decision_node", hr_decision_node)
    
    # 3. Define Entry and Edges
    workflow.set_entry_point("resume_node")
    
    # Conditional routing after parsing
    workflow.add_conditional_edges("resume_node", should_continue)
    
    # Sequential processing
    workflow.add_edge("match_node", "gap_node")
    workflow.add_edge("gap_node", "decision_node")
    workflow.add_edge("decision_node", END)
    
    # 4. Compile application
    return workflow.compile()

def main():
    parser = argparse.ArgumentParser(description="HR Candidate Screening Support Assistant")
    parser.add_argument("--resume", type=str, required=True, help="Path to the candidate's PDF resume")
    parser.add_argument("--job", type=str, required=True, help="Job title to match against")
    args = parser.parse_args()

    logger.info("="*50)
    logger.info(f"STARTING HR SCREENING WORKFLOW")
    logger.info(f"Target Job: {args.job}")
    logger.info(f"Target Resume: {args.resume}")
    logger.info("="*50)
    
    # Initialize the Global State Context
    initial_state = {
        "input_resume_path": args.resume,
        "job_description": args.job,
        "candidate_profile": {},
        "match_result": {},
        "gap_analysis": {},
        "final_output": ""
    }

    # Execute workflow
    app = build_graph()
    try:
        final_state = app.invoke(initial_state)
        
        # If parsing failed, don't generate report
        if "error" in final_state.get("candidate_profile", {}):
            logger.error("Workflow terminated early with errors. No report generated.")
            return

        # Execute final Real-World Tool to save report
        logger.info("Workflow complete. Generating final PDF report...")
        report_path = generate_pdf_report(final_state)
        logger.info(f"Final output saved to {report_path}")

    except Exception as e:
        logger.error(f"Critical Orchestrator Error: {str(e)}")

if __name__ == "__main__":
    main()
