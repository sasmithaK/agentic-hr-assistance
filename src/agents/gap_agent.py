from typing import Dict, Any, List
from langchain_ollama import ChatOllama
from src.state.graph_state import AgentState
from src.tools.search_tools import search_web
from src.utils.logger import logger

class GapAnalysisAgent:
    """
    Agent 3: Gap Analysis Agent
    Identifies missing skills and searches for learning resources to fill those gaps.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.persona = """
        You are a Learning and Development Specialist. Your task is to identify skill gaps 
        and recommend learning resources to help candidates improve their qualifications.
        Be practical, encouraging, and specific in your recommendations.
        """

    def process(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Agent Node: Gap Analysis Agent starting...")
        
        job_title = state.get("job_description", "")
        match_result = state.get("match_result", {})
        candidate_profile = state.get("candidate_profile", {})
        
        # Extract missing skills from previous agent's analysis
        missing_skills = match_result.get("missing_skills", [])
        
        if not missing_skills:
            logger.info("No missing skills found. Gap analysis not needed.")
            return {"gap_analysis": {"status": "No gaps identified", "recommendations": []}}
        
        logger.info(f"Analyzing gaps for {len(missing_skills)} missing skills: {missing_skills}")
        
        # Search for learning resources for each missing skill
        learning_resources = {}
        for skill in missing_skills:
            search_query = f"learn {skill} online tutorial course"
            search_results = search_web(search_query, max_results=3)
            learning_resources[skill] = search_results
        
        # Use LLM to analyze gaps and provide recommendations
        prompt = f"""
        {self.persona}
        
        JOB TITLE: {job_title}
        CANDIDATE NAME: {candidate_profile.get('name', 'N/A')}
        MISSING SKILLS: {', '.join(missing_skills)}
        
        LEARNING RESOURCES FOUND:
        {self._format_learning_resources(learning_resources)}
        
        TASK:
        1. Analyze the skill gaps critically
        2. Prioritize which skills are most important to learn first
        3. Provide specific, actionable recommendations
        4. Suggest a realistic learning timeline
        
        Respond ONLY in the following JSON format:
        {{
            "gap_severity": "<low|medium|high>",
            "priority_skills": [<most important skills to learn first>],
            "recommendations": [<specific actionable advice>],
            "learning_timeline": "<estimated time to fill gaps>",
            "overall_assessment": "<brief summary of gap analysis>"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            
            # Parse JSON response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
            else:
                # Fallback if LLM fails to return JSON
                analysis_result = {
                    "gap_severity": "medium",
                    "priority_skills": missing_skills,
                    "recommendations": ["Focus on learning the missing skills through online courses"],
                    "learning_timeline": "2-3 months",
                    "overall_assessment": "Candidate has potential but needs skill development"
                }
            
            # Add learning resources to the result
            analysis_result["learning_resources"] = learning_resources
            
            logger.info(f"Agent Output: Gap analysis completed - Severity: {analysis_result.get('gap_severity')}")
            return {"gap_analysis": analysis_result}
            
        except Exception as e:
            logger.error(f"Agent Error: {str(e)}")
            return {"gap_analysis": {"error": str(e), "status": "Analysis failed"}}
    
    def _format_learning_resources(self, resources: Dict[str, List[str]]) -> str:
        """Helper method to format learning resources for the prompt."""
        formatted = ""
        for skill, results in resources.items():
            formatted += f"\n{skill}:\n"
            for i, result in enumerate(results, 1):
                formatted += f"  {i}. {result}\n"
        return formatted

# Function to be used as a node in LangGraph
def gap_analysis_node(state: AgentState) -> Dict[str, Any]:
    agent = GapAnalysisAgent()
    return agent.process(state)
