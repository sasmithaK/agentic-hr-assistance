from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.graph_state import GraphState
from src.utils.logger import get_agent_logger

logger = get_agent_logger("DecisionAgent")

def hr_decision_node(state: GraphState) -> GraphState:
    """
    The HR Decision Agent node that intakes parsed data, job matches, and gap analysis
    to generate a final hiring recommendation using Ollama (llama3). 
    It ensures no hallucinations by strictly synthesizing the provided state data.
    
    Args:
        state (GraphState): The LangGraph global context object.
        
    Returns:
        GraphState: The updated global state with the `final_decision` populated.
    """
    logger.info(f"Starting Decision Agent evaluation for {state.get('applicant_name', 'Unknown')}")
    
    # 1. Initialize our local LLM 
    # Using llama3:8b as per assignment default. 
    # temperature=0 to drastically reduce hallucination and ensure factual synthesis of input data
    llm = ChatOllama(model="llama3", temperature=0.0)

    # 2. Design the Persona & Constraints System Prompt (Requirement #1)
    # Using strict rules to prevent hallucination.
    system_prompt = """You are an elite, evidence-based Senior HR Executive. 
    Your objective is to provide a FINAL DECISION (Hire / Reject / Interview) for a candidate.
    
    CRITICAL CONSTRAINTS:
    1. SYNTHESIZE ONLY: You must ONLY use the provided Parse Data, Matching Matrix, and Gap Analysis. 
    2. ZERO HALLUCINATION: Do NOT invent missing skills or candidate experience under any circumstances.
    3. FORMATTING: You must structure your output strictly with the following headers:
       - SUMMARY
       - JUSTIFICATION
       - RECOMMENDATION
       
    Provide a clear, unbiased assessment based purely on facts."""

    # 3. Assemble the prompt context from global State
    user_content = f"""
    Please evaluate the following candidate for the "{state.get('target_job')}" position.
    
    --- DATA TO SYNTHESIZE ---
    APPLICANT NAME: {state.get('applicant_name')}
    
    PARSED RESUME: 
    {state.get('parsed_resume_text', 'No parsed data provided.')}
    
    JOB MATCHING MATRIX:
    {state.get('job_matching_matrix', 'No matching matrix provided.')}
    
    GAP ANALYSIS REPORT:
    {state.get('gap_analysis_report', 'No gap analysis provided.')}
    --------------------------
    
    Based ONLY on the data provided above, generate your FINAL DECISION report following the required FORMATTING constraints.
    """
    
    try:
        # 4. Invoke LLM and capture output
        logger.info("Calling local Llama3 model via ChatOllama...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        response = llm.invoke(messages)
        final_decision_text = response.content
        
        # 5. Update State robustly
        state["final_decision"] = final_decision_text
        logger.info("Successfully generated Final HR Decision")
        
    except Exception as e:
        logger.error(f"Agent failed to generate decision: {str(e)}")
        state["final_decision"] = f"CRITICAL SYSTEM ERROR in Decision Agent: {str(e)}"
        
    return state
