from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.graph_state import AgentState
from src.tools.file_tools import read_resume_pdf
from src.utils.logger import get_agent_logger
import json
import re

logger = get_agent_logger("ResumeAgent")

class ResumeParsingAgent:
    """
    Agent 1: Resume Parsing Agent
    Responsible for converting a raw PDF resume into a structured candidate profile.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0.0)
        self.persona = """
        You are a highly analytical HR Data Extraction Specialist. 
        Your task is to extract structured information from raw resume text.
        
        CRITICAL CONSTRAINTS:
        1. Extract ONLY from the text provided. Do not guess or hallucinate any skills or experience.
        2. Respond ONLY in the following JSON format:
        {
            "name": "<Candidate Full Name>",
            "skills": ["<Skill 1>", "<Skill 2>", ...],
            "experience_years": <Total years of experience as an integer>,
            "education": "<Highest qualification, e.g. BSc Computer Science, University of X>",
            "role": "<Current or most recent job title>"
        }
        """

    def process(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Agent Node: Resume Parsing Agent starting...")
        
        filepath = state.get("input_resume_path", "")
        if not filepath:
            logger.error("No input resume path provided.")
            return {"candidate_profile": {"error": "No resume path provided"}}
            
        # 1. Use real-world tool to extract text
        raw_text = read_resume_pdf(filepath)
        
        if raw_text.startswith("Error"):
            logger.error(f"Failed to read PDF: {raw_text}")
            # If we fail to read, return error dict to let graph short-circuit or handle it
            return {"candidate_profile": {"error": raw_text}}
            
        # 2. Use LLM to structure the data
        prompt = f"""
        {self.persona}
        
        RAW RESUME TEXT:
        -----------------
        {raw_text[:3000]}  # limit context to first 3000 chars to save tokens if it's very long
        -----------------
        """
        
        try:
            logger.info("Calling local Llama3 model via ChatOllama for extraction...")
            messages = [
                SystemMessage(content=self.persona),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            
            # 3. Parse JSON output securely
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                candidate_profile = json.loads(json_match.group())
            else:
                logger.warning("LLM failed to output JSON, falling back to empty profile.")
                candidate_profile = {
                    "name": "Unknown",
                    "skills": [],
                    "experience_years": 0,
                    "role": "Unknown"
                }
                
            logger.info(f"Agent Output: Successfully parsed profile for {candidate_profile.get('name', 'Unknown')}")
            return {"candidate_profile": candidate_profile}
            
        except Exception as e:
            logger.error(f"Agent Error: {str(e)}")
            return {"candidate_profile": {"error": str(e)}}

# LangGraph node entrypoint
def resume_parsing_node(state: AgentState, model_name: str = "llama3:8b") -> AgentState:
    agent = ResumeParsingAgent(model_name=model_name)
    result = agent.process(state)
    state["candidate_profile"] = result.get("candidate_profile", {})
    return state
