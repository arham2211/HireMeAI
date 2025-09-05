import pandas as pd
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
from langchain.tools import tool
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Utility: Read PDF text from resume
def extract_resume_text(folder_name):
    resume_path = f"./CV_and_Resume_Types/{folder_name}/Arham_Affan.pdf"
    if not os.path.exists(resume_path):
        return None
    with fitz.open(resume_path) as doc:
        return "\n".join([page.get_text() for page in doc])

# Utility: Call Groq LLM to assess ATS-friendliness
def get_ats_feedback(job_description, resume_text):
    if not resume_text:
        return "❌ Resume not found"

    prompt = f"""
You are an ATS (Applicant Tracking System) resume evaluator.

Job Description:
{job_description}

Resume:
{resume_text}

Task:
Analyze how well this resume is aligned with the job description. Score its ATS-friendliness from 0 to 10, and explain in 2-3 sentences why.

Give your answer in the format:
Score: X/10
Reason: <short explanation>
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# Main function to process and update the CSV
@tool("update_csv_with_ats_feedback")
def update_csv_with_ats_feedback() -> str:
    """Reads a CSV file of job descriptions,and then give a ats feedback for each job description against the resumes in the CVs(matched folder)"""
    csv_path = "linkedin_jobs_with_matches.csv"
    output_csv = "final_output.csv"

    df = pd.read_csv(csv_path)

    ats_feedback_list = []

    for i, row in df.iterrows():
        job_desc = row.get("job_description", "")
        folder = row.get("matched_folder", "").strip().upper()

        print(f"🔍 Processing row {i + 1}: Folder={folder}")

        resume_text = extract_resume_text(folder)
        feedback = get_ats_feedback(job_desc, resume_text)
        print(f"✅ Feedback: {feedback[:100]}...\n")

        ats_feedback_list.append(feedback)
        time.sleep(5)  # Optional: prevent rate-limiting

    df["ats_feedback"] = ats_feedback_list
    df.to_csv(output_csv, index=False)
    print(f"✅ Final output saved at: {output_csv}")

    # Delete the original file
    if os.path.exists(csv_path):
        os.remove(csv_path)
        

    return output_csv

