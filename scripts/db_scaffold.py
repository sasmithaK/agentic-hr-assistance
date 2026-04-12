import sqlite3
import os

DB_FILENAME = "local_data/hr_database.db"

def scaffold_db():
    os.makedirs(os.path.dirname(DB_FILENAME), exist_ok=True)
    
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    # Create a table for job skills matrices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT UNIQUE NOT NULL,
            core_skills TEXT NOT NULL,
            experience_years INTEGER NOT NULL
        )
    """)
    
    # Insert some dummy sample data if it doesn't exist
    try:
        cursor.execute("INSERT INTO job_requirements (job_title, core_skills, experience_years) VALUES (?, ?, ?)",
                       ("Software Engineer", "Python, React, SQL, Git", 3))
        cursor.execute("INSERT INTO job_requirements (job_title, core_skills, experience_years) VALUES (?, ?, ?)",
                       ("Data Scientist", "Python, Pandas, SQL, Machine Learning", 2))
        conn.commit()
        print(f"✅ Successfully scaffolded SQLite HR Database at {DB_FILENAME}!")
    except sqlite3.IntegrityError:
        print(f"ℹ️ Database at {DB_FILENAME} already scaffolded.")
        
    conn.close()

if __name__ == "__main__":
    scaffold_db()
