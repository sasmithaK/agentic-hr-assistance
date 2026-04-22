import os
from fpdf import FPDF
from typing import Dict, Any

from src.state.graph_state import AgentState
from src.utils.logger import get_agent_logger
from pypdf import PdfReader

logger = get_agent_logger("FileTools")

def generate_pdf_report(state: AgentState) -> str:
    """
    A custom tool that generates an automated, securely saved PDF report of the final HR decision.
    
    Args:
        state (AgentState): The current global state of the LangGraph workflow containing candidate 
                            data, the target job, and the final decision text.
                            
    Returns:
        str: Absolute or relative filepath pointing to the successfully created PDF report, 
             or an error string if generation failed.
    """
    candidate_name = state.get("candidate_profile", {}).get("name", "Unknown_Applicant")
    logger.info(f"Generating PDF report for applicant: {candidate_name}")
    try:
        output_dir = os.path.join("local_data", "output_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        target_job = state.get("job_description", "Unknown_Job")
        final_decision = state.get("final_output", "No final decision provided.")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Add Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"HR Assessment Report: {candidate_name}", new_x="LMARGIN", new_y="NEXT", align='C')
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
        
        filename = f"{candidate_name.replace(' ', '_')}_{target_job.replace(' ', '_')}_report.pdf"
        filepath = os.path.join(output_dir, filename)
        
        pdf.output(filepath)
        logger.info(f"Successfully saved PDF report at: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return f"Error: Failed to generate PDF report -> {str(e)}"

def read_resume_pdf(filepath: str) -> str:
    """
    Reads a PDF resume and extracts the raw text.
    
    Args:
        filepath (str): The path to the PDF file to read.
        
    Returns:
        str: The extracted text from the PDF, or an error message.
    """
    logger.info(f"Tool Invoke: read_resume_pdf | Args: filepath='{filepath}'")
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        reader = PdfReader(filepath)
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
                
        extracted_text = "\n".join(text_content)
        logger.info(f"Tool Output: Successfully extracted {len(extracted_text)} characters from {filepath}")
        return extracted_text
        
    except Exception as e:
        logger.error(f"Tool Error: {str(e)}")
        return f"Error reading PDF: {str(e)}"

