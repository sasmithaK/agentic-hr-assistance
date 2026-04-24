import argparse
import os
import sys

# Add project root to sys.path to allow absolute imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from src.state.graph_state import AgentState
from src.agents.resume_agent import resume_parsing_node
from src.agents.match_agent import job_matching_node
from src.agents.gap_agent import gap_analysis_node
from src.agents.decision_agent import hr_decision_node
from src.tools.file_tools import generate_pdf_report
from src.tools.reporting_tools import generate_ranked_csv, generate_score_graphs
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

def build_graph(model_name: str = "llama3:8b"):
    """
    Builds the LangGraph StateGraph mapping the HR candidate screening workflow.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("resume_node", lambda s: resume_parsing_node(s, model_name))
    workflow.add_node("match_node", lambda s: job_matching_node(s, model_name))
    workflow.add_node("gap_node", lambda s: gap_analysis_node(s, model_name))
    workflow.add_node("decision_node", lambda s: hr_decision_node(s, model_name))
    
    workflow.set_entry_point("resume_node")
    workflow.add_conditional_edges("resume_node", should_continue)
    workflow.add_edge("match_node", "gap_node")
    workflow.add_edge("gap_node", "decision_node")
    workflow.add_edge("decision_node", END)
    
    return workflow.compile()

def run_single(resume_path: str, jd_path: str, app) -> AgentState:
    """
    Runs the LangGraph pipeline for a single resume file.
    """
    logger.info(f"Processing resume: {resume_path}")
    initial_state = {
        "input_resume_path": resume_path,
        "job_description": jd_path,   # Now a file path, not a job title string
        "candidate_profile": {},
        "match_result": {},
        "gap_analysis": {},
        "final_output": ""
    }
    try:
        final_state = app.invoke(initial_state)
        if "error" not in final_state.get("candidate_profile", {}):
            pdf_path = generate_pdf_report(final_state)
            logger.info(f"Individual PDF saved to: {pdf_path}")
        return final_state
    except Exception as e:
        logger.error(f"Failed to process {resume_path}: {str(e)}")
        return initial_state

def main():
    parser = argparse.ArgumentParser(description="HR Candidate Screening Support Assistant")
    
    # Batch mode (recommended)
    parser.add_argument("--folder", type=str, help="Path to a folder containing multiple PDF resumes")
    
    # Single mode (backwards compatible)
    parser.add_argument("--resume", type=str, help="Path to a single candidate PDF resume")
    
    # Required: JD file path
    parser.add_argument("--jd", type=str, required=True, help="Path to the Job Description .txt or .md file")
    
    # Optional: model selection
    parser.add_argument("--model", type=str, default="llama3:8b",
                        help="Ollama model to use (e.g. phi3, llama3:8b). Default: llama3:8b")
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("STARTING HR SCREENING WORKFLOW")
    logger.info(f"Job Description File: {args.jd}")
    logger.info(f"LLM Model: {args.model}")
    logger.info("=" * 50)

    app = build_graph(model_name=args.model)

    # ── BATCH MODE ──────────────────────────────────────────────
    if args.folder:
        if not os.path.isdir(args.folder):
            logger.error(f"Folder not found: {args.folder}")
            return

        pdf_files = [f for f in os.listdir(args.folder) if f.lower().endswith(".pdf")]
        
        if not pdf_files:
            logger.error("No PDF files found in the specified folder.")
            return
        
        logger.info(f"Batch mode: Found {len(pdf_files)} resume(s) to process.")
        all_results = []
        
        for pdf_file in pdf_files:
            resume_path = os.path.join(args.folder, pdf_file)
            result = run_single(resume_path, args.jd, app)
            all_results.append(result)
        
        # ── Batch Reporting (Decision Agent reporting tools) ──
        logger.info("All resumes processed. Generating batch reports...")
        csv_path = generate_ranked_csv(all_results)
        graph_path = generate_score_graphs(all_results)
        logger.info(f"Master CSV saved: {csv_path}")
        logger.info(f"Score chart saved: {graph_path}")
        logger.info("Batch workflow complete.")

    # ── SINGLE MODE ─────────────────────────────────────────────
    elif args.resume:
        result = run_single(args.resume, args.jd, app)
        if "error" not in result.get("candidate_profile", {}):
            logger.info("Single resume workflow complete.")
        else:
            logger.error("Single resume workflow terminated early.")
    
    else:
        logger.error("Please provide either --folder or --resume argument.")

if __name__ == "__main__":
    main()
