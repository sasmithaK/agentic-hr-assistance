from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.graph_state import AgentState
from src.utils.logger import get_agent_logger
import json

logger = get_agent_logger("DecisionAgent")

def hr_decision_node(state: AgentState) -> AgentState:
    """
    The HR Decision Agent node that intakes parsed data, job matches, and gap analysis
    to generate a final hiring recommendation using Ollama (llama3). 
    It ensures no hallucinations by strictly synthesizing the provided state data.
    
    Args:
        state (AgentState): The LangGraph global context object.
        
    Returns:
        AgentState: The updated global state with the `final_output` populated.
    """
    candidate_name = state.get("candidate_profile", {}).get("name", "Unknown")
    logger.info(f"Starting Decision Agent evaluation for {candidate_name}")
    
    # 1. Initialize our local LLM 
    # Using llama3:8b as per assignment default. 
    # temperature=0 to drastically reduce hallucination and ensure factual synthesis of input data
    llm = ChatOllama(model="llama3:8b", temperature=0.0)

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
    Please evaluate the following candidate for the "{state.get('job_description', 'Unknown Position')}" position.
    
    --- DATA TO SYNTHESIZE ---
    APPLICANT NAME: {candidate_name}
    
    PARSED RESUME: 
    {json.dumps(state.get('candidate_profile', {}), indent=2)}
    
    JOB MATCHING MATRIX:
    {json.dumps(state.get('match_result', {}), indent=2)}
    
    GAP ANALYSIS REPORT:
    {json.dumps(state.get('gap_analysis', {}), indent=2)}
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
        state["final_output"] = final_decision_text
        logger.info("Successfully generated Final HR Decision")
        
    except Exception as e:
        logger.error(f"Agent failed to generate decision: {str(e)}")
        state["final_output"] = f"CRITICAL SYSTEM ERROR in Decision Agent: {str(e)}"
        
    return state
