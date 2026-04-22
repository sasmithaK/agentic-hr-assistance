import json
import re
from typing import Dict, Any
from langchain_ollama import ChatOllama
from src.state.graph_state import AgentState
from src.tools.file_tools import read_job_description
from src.utils.logger import get_agent_logger

logger = get_agent_logger("MatchAgent")

class JobMatchingAgent:
    """
    Agent 2: Job Matching Agent
    Responsible for semantically comparing a candidate's profile against a
    Job Description file, returning a 0-100 match score with reasoning.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.persona = """You are a Precision-oriented HR Data Analyst.
        Your task is to calculate the alignment between a candidate's profile and a full Job Description.
        Be objective, thorough, and strictly quantitative in your assessment.
        You MUST return valid JSON only — no extra text, no markdown fences."""

    def process(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Agent Node: Job Matching Agent starting...")
        
        jd_filepath = state.get("job_description", "")
        candidate_profile = state.get("candidate_profile", {})
        candidate_skills = candidate_profile.get("skills", [])
        
        # 1. Tool: Read the full Job Description from file (real-world file interaction)
        jd_text = read_job_description(jd_filepath)
        
        if jd_text.startswith("Error:"):
            logger.error(f"Failed to read JD file: {jd_text}")
            return {"match_result": {"match_score": 0, "matched_skills": [], "missing_skills": [], "reasoning": jd_text}}

        # 2. Use LLM for semantic, context-aware comparison against the full JD
        prompt = f"""
        {self.persona}
        
        ===JOB DESCRIPTION===
        {jd_text}
        =====================
        
        CANDIDATE NAME: {candidate_profile.get('name', 'N/A')}
        CANDIDATE SKILLS: {', '.join(candidate_skills)}
        CANDIDATE EXPERIENCE: {candidate_profile.get('experience_years', 'N/A')} years
        CANDIDATE EDUCATION: {candidate_profile.get('education', 'N/A')}
        
        TASK:
        1. Read the full Job Description carefully.
        2. Identify which candidate skills MATCH the JD requirements.
        3. Identify which key JD requirements the candidate is MISSING.
        4. Calculate an overall match_score (integer from 0 to 100) based on skill and experience fit.
        
        Return ONLY this JSON (no markdown, no extra text):
        {{
            "match_score": <integer 0-100>,
            "matched_skills": ["<skill>"],
            "missing_skills": ["<skill>"],
            "reasoning": "<one sentence explanation of score>"
        }}
        """
        
        try:
            logger.info("Calling local Llama3 model via ChatOllama for semantic JD matching...")
            response = self.llm.invoke(prompt)
            
            # Robustly extract JSON from LLM response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # Enforce match_score as an integer
                result["match_score"] = int(result.get("match_score", 0))
            else:
                result = {
                    "match_score": 0,
                    "matched_skills": [],
                    "missing_skills": [],
                    "reasoning": "LLM failed to output valid JSON."
                }
                
            logger.info(f"Agent Output: Calculated Match Score: {result.get('match_score')}%")
            return {"match_result": result}
            
        except Exception as e:
            logger.error(f"Agent Error: {str(e)}")
            return {"match_result": {"match_score": 0, "error": str(e)}}

# LangGraph node entrypoint
def job_matching_node(state: AgentState, model_name: str = "llama3:8b") -> AgentState:
    agent = JobMatchingAgent(model_name=model_name)
    return agent.process(state)

