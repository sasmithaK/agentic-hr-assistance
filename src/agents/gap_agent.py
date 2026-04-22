from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.graph_state import AgentState
from src.tools.search_tools import search_duckduckgo
from src.utils.logger import get_agent_logger
import json
import re

logger = get_agent_logger("GapAgent")

class GapAnalysisAgent:
    """
    Agent 3: Gap Analysis Agent
    Responsible for identifying the severity of missing skills and checking context 
    using the DuckDuckGo search tool if certain candidate skills are unfamiliar.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0.0)
        self.persona = """
        You are a highly analytical HR Technical Assessor.
        Your job is to perform a gap analysis on a candidate based on their match results.
        
        CRITICAL CONSTRAINTS:
        1. If you are uncertain about a skill, use web search context (if provided).
        2. DO NOT invent skills.
        3. Respond ONLY in the following JSON format:
        {
            "strengths": ["<strength 1>", "<strength 2>"],
            "weaknesses": ["<weakness 1>", "<weakness 2>"],
            "risk_level": "<Low | Medium | High>",
            "analysis_summary": "<Short sentence summarizing the gap>"
        }
        """

    def process(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Agent Node: Gap Analysis Agent starting...")
        
        job_title = state.get("job_description", "")
        match_result = state.get("match_result", {})
        missing_skills = match_result.get("missing_skills", [])
        
        # 1. Use Tool: Search web for context on the most critical missing skill or unknown elements
        web_context = ""
        if missing_skills:
            # Pick the first missing skill to search for its importance in the role
            query = f"Importance of {missing_skills[0]} for {job_title}"
            logger.info(f"Using search tool to contextualize missing skill: {missing_skills[0]}")
            search_results = search_duckduckgo(query)
            
            if search_results:
                web_context = "WEB SEARCH CONTEXT FOR MISSING SKILL:\n"
                for r in search_results:
                    web_context += f"- {r.get('body', '')}\n"
        
        # 2. Prepare LLM prompt
        prompt = f"""
        {self.persona}
        
        JOB TITLE: {job_title}
        MATCH SCORE: {match_result.get('match_score', 0)}%
        MATCHED SKILLS: {', '.join(match_result.get('matched_skills', []))}
        MISSING SKILLS: {', '.join(missing_skills)}
        
        {web_context}
        
        TASK: Output the final gap analysis JSON based on the above data.
        """
        
        try:
            logger.info("Calling local Llama3 model via ChatOllama for gap analysis...")
            messages = [
                SystemMessage(content=self.persona),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            
            # 3. Parse JSON output securely
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                gap_analysis = json.loads(json_match.group())
            else:
                logger.warning("LLM failed to output JSON, falling back to manual error extraction.")
                gap_analysis = {
                    "strengths": match_result.get('matched_skills', []),
                    "weaknesses": missing_skills,
                    "risk_level": "High" if match_result.get('match_score', 0) < 50 else "Medium",
                    "analysis_summary": "Failed to parse LLM structured output."
                }
                
            logger.info(f"Agent Output: Gap Analysis Risk Level -> {gap_analysis.get('risk_level', 'Unknown')}")
            return {"gap_analysis": gap_analysis}
            
        except Exception as e:
            logger.error(f"Agent Error: {str(e)}")
            return {"gap_analysis": {"error": str(e)}}

# LangGraph node entrypoint
def gap_analysis_node(state: AgentState, model_name: str = "llama3:8b") -> AgentState:
    agent = GapAnalysisAgent(model_name=model_name)
    result = agent.process(state)
    state["gap_analysis"] = result.get("gap_analysis", {})
    return state
