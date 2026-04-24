import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from src.utils.logger import get_agent_logger

logger = get_agent_logger("ReportingTools")

def generate_ranked_csv(candidates: List[Dict[str, Any]]) -> str:
    """
    Takes a batch of processed candidate states, ranks them by match score,
    and exports a summarized CSV report for HR.
    """
    logger.info(f"Tool Invoke: generate_ranked_csv | Processing {len(candidates)} candidates.")
    try:
        output_dir = os.path.join("local_data", "output_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        data = []
        for state in candidates:
            profile = state.get("candidate_profile", {})
            name = profile.get("name", "Unknown")
            
            # Safely extract numerical score
            score = 0
            match_res = state.get("match_result", {})
            if isinstance(match_res, dict):
                score = match_res.get("match_score", 0)
            elif isinstance(match_res, (int, float)):
                score = match_res
                
            risk = state.get("gap_analysis", {}).get("risk_level", "Unknown")
            
            data.append({
                "Candidate Name": name,
                "Match Score (%)": score,
                "Risk Level": risk,
                "Final Decision": state.get("final_output", "Pending")
            })
            
        df = pd.DataFrame(data)
        # Sort from highest to lowest score
        df = df.sort_values(by="Match Score (%)", ascending=False).reset_index(drop=True)

        # ── Analytics Summary ──────────────────────────────────────
        avg_score = df["Match Score (%)"].mean()
        top_candidate = df.iloc[0]["Candidate Name"] if not df.empty else "N/A"
        hire_count = df["Final Decision"].str.contains("Hire", case=False, na=False).sum()
        interview_count = df["Final Decision"].str.contains("Interview", case=False, na=False).sum()
        reject_count = df["Final Decision"].str.contains("Reject", case=False, na=False).sum()

        summary_df = pd.DataFrame([
            {"Candidate Name": "── ANALYTICS SUMMARY ──", "Match Score (%)": "", "Risk Level": "", "Final Decision": ""},
            {"Candidate Name": "Average Match Score", "Match Score (%)": f"{avg_score:.1f}%", "Risk Level": "", "Final Decision": ""},
            {"Candidate Name": "Top Candidate", "Match Score (%)": "", "Risk Level": "", "Final Decision": top_candidate},
            {"Candidate Name": "Shortlisted (Hire)", "Match Score (%)": hire_count, "Risk Level": "", "Final Decision": ""},
            {"Candidate Name": "For Interview", "Match Score (%)": interview_count, "Risk Level": "", "Final Decision": ""},
            {"Candidate Name": "Rejected", "Match Score (%)": reject_count, "Risk Level": "", "Final Decision": ""},
        ])

        final_df = pd.concat([df, summary_df], ignore_index=True)
        filepath = os.path.join(output_dir, "Master_Ranking_Overview.csv")
        final_df.to_csv(filepath, index=False)
        
        logger.info(f"Tool Output: CSV successfully generated at {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Tool Error: Failed to generate CSV -> {str(e)}")
        return f"Error generating CSV: {str(e)}"

def generate_score_graphs(candidates: List[Dict[str, Any]]) -> str:
    """
    Generates a visual bar chart comparing candidate match scores using matplotlib.
    """
    logger.info(f"Tool Invoke: generate_score_graphs | Processing {len(candidates)} candidates.")
    try:
        output_dir = os.path.join("local_data", "output_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        names = []
        scores = []
        
        for state in candidates:
            name = state.get("candidate_profile", {}).get("name", "Unknown")
            score = 0
            match_res = state.get("match_result", {})
            if isinstance(match_res, dict):
                score = match_res.get("match_score", 0)
            elif isinstance(match_res, (int, float)):
                score = match_res
                
            # If name is unknown and score is 0, they failed parsing, but we graph them anyway
            names.append(name)
            scores.append(float(score))
            
        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, scores, color=['#4CAF50' if s >= 70 else '#FFC107' if s >= 40 else '#F44336' for s in scores])
        
        plt.title('Candidate Match Score Comparison', fontsize=16)
        plt.xlabel('Candidates', fontsize=12)
        plt.ylabel('Match Score (%)', fontsize=12)
        plt.ylim(0, 100)
        plt.xticks(rotation=45, ha='right')
        
        # Add exact values on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{int(yval)}%', ha='center', va='bottom')
            
        plt.tight_layout()
        
        filepath = os.path.join(output_dir, "Candidate_Scores_Chart.png")
        plt.savefig(filepath)
        plt.close()
        
        logger.info(f"Tool Output: Graph successfully generated at {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Tool Error: Failed to generate Graph -> {str(e)}")
        return f"Error generating Graph: {str(e)}"
