from typing import Dict, Any, List
from langchain_ollama import ChatOllama
import json
import re

class LLMEvaluator:
    """
    LLM-as-a-Judge evaluator for validating agent outputs
    and detecting hallucinations in gap analysis results.
    """
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.judge_persona = """
        You are an expert evaluator for AI-generated content. Your task is to analyze 
        gap analysis outputs for accuracy, completeness, and potential hallucinations.
        Be thorough, objective, and provide specific feedback.
        """

    def evaluate_gap_analysis(self, gap_analysis: Dict[str, Any], 
                           missing_skills: List[str], 
                           job_title: str) -> Dict[str, Any]:
        """
        Evaluate gap analysis output for accuracy and hallucinations.
        
        Args:
            gap_analysis: The gap analysis output to evaluate
            missing_skills: List of actual missing skills
            job_title: The job title being analyzed
            
        Returns:
            Dict with evaluation results including score and issues found
        """
        prompt = f"""
        {self.judge_persona}
        
        JOB TITLE: {job_title}
        ACTUAL MISSING SKILLS: {', '.join(missing_skills)}
        
        GAP ANALYSIS OUTPUT TO EVALUATE:
        {json.dumps(gap_analysis, indent=2)}
        
        EVALUATION TASK:
        1. Check if all priority_skills are actually in the missing_skills list
        2. Verify gap_severity is appropriate for the number of missing skills
        3. Assess if recommendations are practical and actionable
        4. Check for any hallucinated skills or information
        5. Evaluate overall quality and coherence
        
        Respond ONLY in this JSON format:
        {{
            "score": <0-100>,
            "hallucinations_detected": <true/false>,
            "issues_found": [<specific issues identified>],
            "strengths": [<positive aspects of the output>],
            "overall_assessment": "<brief evaluation summary>"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "score": 50,
                    "hallucinations_detected": True,
                    "issues_found": ["Failed to parse evaluation response"],
                    "strengths": [],
                    "overall_assessment": "Evaluation failed due to parsing error"
                }
        except Exception as e:
            return {
                "score": 0,
                "hallucinations_detected": True,
                "issues_found": [f"Evaluation error: {str(e)}"],
                "strengths": [],
                "overall_assessment": "Evaluation failed due to error"
            }

    def evaluate_learning_resources(self, learning_resources: Dict[str, List[str]], 
                                missing_skills: List[str]) -> Dict[str, Any]:
        """
        Evaluate the quality and relevance of learning resources.
        
        Args:
            learning_resources: Dictionary of skills and their learning resources
            missing_skills: List of skills that need resources
            
        Returns:
            Dict with evaluation results
        """
        prompt = f"""
        {self.judge_persona}
        
        MISSING SKILLS: {', '.join(missing_skills)}
        
        LEARNING RESOURCES TO EVALUATE:
        {json.dumps(learning_resources, indent=2)}
        
        EVALUATION TASK:
        1. Check if all missing skills have learning resources
        2. Assess relevance and quality of resources
        3. Verify resources are practical for skill development
        4. Check for completeness of coverage
        
        Respond ONLY in this JSON format:
        {{
            "coverage_score": <0-100>,
            "relevance_score": <0-100>,
            "quality_issues": [<specific quality problems>],
            "missing_resources": [<skills without adequate resources>],
            "overall_quality": "<brief quality assessment>"
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "coverage_score": 50,
                    "relevance_score": 50,
                    "quality_issues": ["Failed to parse evaluation response"],
                    "missing_resources": missing_skills,
                    "overall_quality": "Evaluation failed due to parsing error"
                }
        except Exception as e:
            return {
                "coverage_score": 0,
                "relevance_score": 0,
                "quality_issues": [f"Evaluation error: {str(e)}"],
                "missing_resources": missing_skills,
                "overall_quality": "Evaluation failed due to error"
            }
