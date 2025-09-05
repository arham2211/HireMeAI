# HireMeAI 🚀

HireMeAI is an **AI-powered job scraping and resume analysis pipeline**.  
It scrapes job listings, processes job descriptions, matches them with candidate resumes, and provides **ATS-style feedback** for each candidate.  

The system is powered by **LangChain agents + custom tools**, and runs on a daily basis using **GitHub Actions**.

---

## 🔑 Features
- **Scrape LinkedIn Jobs** → Collects job postings from LinkedIn.
- **Job Matching** → Matches job descriptions with resumes and organizes by skills.
- **ATS Feedback** → Analyzes resumes against job descriptions and generates ATS-style feedback.
- **Automated CSV Pipeline** → Each step reads input CSVs and generates output CSVs for the next stage.
- **Daily Automation** → Configurable GitHub Actions runner executes the pipeline and stores results as artifacts.

---
