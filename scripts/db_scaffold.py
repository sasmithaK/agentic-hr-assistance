import sqlite3
import os

def scaffold_db():
    db_path = "local_data/hr_database.db"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL,
        required_skills TEXT NOT NULL
    )
    ''')
    
    # Insert sample data
    sample_jobs = [
        ("Software Engineer", "Python, LangChain, SQL, Docker, FastAPI"),
        ("Data Scientist", "Python, Machine Learning, Pandas, Scikit-learn, Statistics"),
        ("Cloud Architect", "AWS, Terraform, Kubernetes, Security, Networking"),
        ("HR Manager", "Recruitment, Performance Management, Employee Relations, Communication")
    ]
    
    for title, skills in sample_jobs:
        cursor.execute("INSERT OR IGNORE INTO jobs (title, required_skills) VALUES (?, ?)", (title, skills))
    
    conn.commit()
    conn.close()
    print(f"Database initialized and seeded at {db_path}")

if __name__ == "__main__":
    scaffold_db()
