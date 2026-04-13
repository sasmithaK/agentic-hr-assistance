from typing import Dict, Any
from langchain_ollama import ChatOllama
from src.state.graph_state import AgentState
from src.tools.database_tools import query_skills_db
from src.utils.logger import logger

class JobMatchingAgent:
    """
    Agent 2: Job Matching Agent
    Responsible for comparing candidate skills with the required skills for a role.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.persona = """
        You are a Precision-oriented HR Data Analyst. Your task is to calculate the alignment between a candidate's profile and the job's required skills.
        Be objective, thorough, and quantitative in your assessment.
        """

    def process(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Agent Node: Job Matching Agent starting...")
        
        job_title = state.get("job_description", "")
        candidate_profile = state.get("candidate_profile", {})
        
        # 1. Retrieve required skills from DB tool
        required_skills = query_skills_db(job_title)
        
        if not required_skills:
            logger.warning(f"No reference skills found for {job_title}. Skipping precise match.")
            return {"match_result": {"score": 0, "matched_skills": [], "status": "No database entry for job title"}}

        candidate_skills = candidate_profile.get("skills", [])
        
        # 2. Use LLM to perform nuanced comparison
        prompt = f"""
        {self.persona}
        
        JOB TITLE: {job_title}
        REQUIRED SKILLS (from Database): {', '.join(required_skills)}
        
        CANDIDATE NAME: {candidate_profile.get('name', 'N/A')}
        CANDIDATE SKILLS: {', '.join(candidate_skills)}
        
        TASK:
        1. Identify which required skills the candidate possesses.
        2. Identify which required skills are missing.
        3. Calculate a match score (0-100%) based on skill coverage.
        
        Respond ONLY in the following JSON format:
        {{
            "match_score": <int>,
            "matched_skills": [<skills found>],
            "missing_skills": [<skills missing>],
            "reasoning": "<short explanation>"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            # In a real scenario, we'd parse the JSON from response.content
            # For simplicity and robustness in this assignment, we use a simple parser
            import json
            import re
            
            # Extract JSON from potential Markdown blocks
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if LLM fails to return JSON
                result = {
                    "match_score": 0,
                    "matched_skills": [],
                    "missing_skills": required_skills,
                    "reasoning": "Failed to parse LLM response"
                }
                
            logger.info(f"Agent Output: Calculated Match Score: {result.get('match_score')}%")
            return {"match_result": result}
            
        except Exception as e:
            logger.error(f"Agent Error: {str(e)}")
            return {"match_result": {"error": str(e)}}

# Function to be used as a node in LangGraph
def job_matching_node(state: AgentState) -> Dict[str, Any]:
    agent = JobMatchingAgent()
    return agent.process(state)
