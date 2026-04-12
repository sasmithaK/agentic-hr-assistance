import os
from fpdf import FPDF
from typing import Dict, Any

from src.state.graph_state import GraphState
from src.utils.logger import get_agent_logger

logger = get_agent_logger("FileTools")

def generate_pdf_report(state: GraphState) -> str:
    """
    A custom tool that generates an automated, securely saved PDF report of the final HR decision.
    
    Args:
        state (GraphState): The current global state of the LangGraph workflow containing candidate 
                            data, the target job, and the final decision text.
                            
    Returns:
        str: Absolute or relative filepath pointing to the successfully created PDF report, 
             or an error string if generation failed.
    """
    logger.info(f"Generating PDF report for applicant: {state.get('applicant_name', 'Unknown')}")
    try:
        output_dir = os.path.join("local_data", "output_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        applicant_name = state.get("applicant_name", "Unknown_Applicant")
        target_job = state.get("target_job", "Unknown_Job")
        final_decision = state.get("final_decision", "No final decision provided.")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Add Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"HR Assessment Report: {applicant_name}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        # Add Job Info
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f"Target Position: {target_job}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        # Add Final Decision section
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Final AI Decision & Recommendation:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        
        # Handle multi-line string safely via multi_cell
        safe_decision = str(final_decision).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, safe_decision)
        
        filename = f"{applicant_name.replace(' ', '_')}_{target_job.replace(' ', '_')}_report.pdf"
        filepath = os.path.join(output_dir, filename)
        
        pdf.output(filepath)
        logger.info(f"Successfully saved PDF report at: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return f"Error: Failed to generate PDF report -> {str(e)}"
