import sqlite3
from typing import List
from src.utils.logger import logger

def query_skills_db(job_title: str) -> List[str]:
    """
    Queries the local SQLite database to retrieve the required skills for a given job title.
    
    Args:
        job_title (str): The official title of the position to query.
        
    Returns:
        List[str]: A list of required skills found in the database. 
                   Returns an empty list if the job title is not found.
    """
    db_path = "local_data/hr_database.db"
    skills = []
    
    logger.info(f"Tool Invoke: query_skills_db | Args: job_title='{job_title}'")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT required_skills FROM jobs WHERE title = ?", (job_title,))
        result = cursor.fetchone()
        
        if result:
            # skills are stored as a comma-separated string
            skills = [s.strip() for s in result[0].split(",")]
            logger.info(f"Tool Output: Successfully retrieved {len(skills)} skills for '{job_title}'")
        else:
            logger.warning(f"Tool Output: No skills found for job title '{job_title}'")
            
        conn.close()
    except Exception as e:
        logger.error(f"Tool Error: {str(e)}")
        
    return skills
