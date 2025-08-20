import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
import os


@tool("scrape_linkedin_jobs")
def scrape_linkedin_jobs() -> str:
    """
    Scrapes job data from LinkedIn using URLs provided in an Excel file.
    Expects the Excel file to have a column named 'Job_URLs'.
    Returns the path to the saved CSV file with job data.
    """
    csv_path = "Job_Names_with_URLs.csv"
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return f"Failed to read Excel file: {e}"

    all_jobs = []

    for list_url in df['Job_URLs']:
        try:
            response = requests.get(list_url)
            list_data = response.text
            list_soup = BeautifulSoup(list_data, "html.parser")
            page_jobs = list_soup.find_all("li")

            id_list = []
            for job in page_jobs:
                base_card_div = job.find("div", {"class": "base-card"})
                if base_card_div and base_card_div.get("data-entity-urn"):
                    job_id = base_card_div.get("data-entity-urn").split(":")[3]
                    id_list.append(job_id)

            for job_id in id_list:
                job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                job_response = requests.get(job_url)
                job_soup = BeautifulSoup(job_response.text, "html.parser")

                job_post = {
                    "job_title": None,
                    "company_name": None,
                    "job_posted": None,
                    "job_description": None,
                    "job_link": None
                }

                try:
                    job_post["job_title"] = job_soup.find("h2", {
                        "class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"
                    }).text.strip()
                except:
                    pass
                try:
                    job_post["company_name"] = job_soup.find("a", {
                        "class": "topcard__org-name-link topcard__flavor--black-link"
                    }).text.strip()
                except:
                    pass
                try:
                    job_post["job_posted"] = job_soup.find("span", {
                        "class": "posted-time-ago__text topcard__flavor--metadata"
                    }).text.strip()
                except:
                    pass
                try:
                    job_post["job_description"] = job_soup.find("div", {
                        "class": "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden"
                    }).text.strip()
                except:
                    pass
                try:
                    job_post["job_link"] = job_soup.find("a", {"class": "topcard__link"}).get("href")
                except:
                    pass

                all_jobs.append(job_post)

        except Exception as e:
            print(f"Failed to scrape {list_url}: {e}")

    job_df = pd.DataFrame(all_jobs).drop_duplicates()
    output_path = "linkedin_jobs.csv"
    job_df.to_csv(output_path, index=False)
    return f"Job scraping completed. Saved to {output_path}"
