from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.graph_state import AgentState
from src.utils.logger import get_agent_logger
import json

logger = get_agent_logger("DecisionAgent")

def hr_decision_node(state: AgentState, model_name: str = "llama3:8b") -> AgentState:
    """
    The HR Decision Agent node that intakes parsed data, job matches, and gap analysis
    to generate a final hiring recommendation using a local Ollama model.
    Accepts model_name to support runtime model switching via --model CLI flag.

    Args:
        state (AgentState): The LangGraph global context object.
        model_name (str): The Ollama model to use. Defaults to llama3:8b.

    Returns:
        AgentState: The updated global state with `final_output` populated.
    """
    candidate_name = state.get("candidate_profile", {}).get("name", "Unknown")
    logger.info(f"Starting Decision Agent evaluation for {candidate_name}")

    # Initialize local LLM with the selected model
    # temperature=0 ensures deterministic, factual synthesis with minimal hallucination
    llm = ChatOllama(model=model_name, temperature=0.0)

    # Strict persona & formatting system prompt
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

    # Assemble full context from global state
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
        logger.info(f"Calling {model_name} via ChatOllama...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        response = llm.invoke(messages)
        state["final_output"] = response.content
        logger.info("Successfully generated Final HR Decision")

    except Exception as e:
        logger.error(f"Agent failed to generate decision: {str(e)}")
        state["final_output"] = f"CRITICAL SYSTEM ERROR in Decision Agent: {str(e)}"

    return state
