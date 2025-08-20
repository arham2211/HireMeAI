from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from langchain_openai import ChatOpenAI  # Updated import
from job_scraper_tool import scrape_linkedin_jobs
from resume_matcher_tool import match_and_process_jobs
from job_scorer_tool import update_csv_with_ats_feedback
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the LLM with updated model name (gpt-4o-mini doesn't exist, using gpt-4-turbo instead)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tools = [
    Tool(
        func=scrape_linkedin_jobs,
        name="scrape_linkedin_jobs",
        description="Scrapes job data from LinkedIn"
    ),
    Tool(
        func=match_and_process_jobs,
        name="match_and_process_jobs",
        description="Matches job descriptions from a CSV file to skill categories and processes resumes accordingly."
    ),
    Tool(
        func = update_csv_with_ats_feedback,
        name = "update_csv_with_ats_feedback",
        description = "Reads a CSV file of job descriptions,and then give a ats feedback for each job description against the resumes in the CVs(matched folder)"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)



agent.invoke("First scrape the linkedin jobs then match and process the jobs, then at then end give their ats scored feedback")
