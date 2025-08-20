from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import time
from dotenv import load_dotenv
import os
from langchain.tools import tool


load_dotenv()


client = OpenAI(
    api_key=os.getenv("A4F_API_KEY"),
    base_url=os.getenv("A4F_BASE_URL"),
)

folder_reference_map = {
    "frontend": "Frontend development focused on client-side interfaces using HTML5, CSS3, JavaScript, TypeScript, React, Angular, Vue.js, Next.js, Redux, responsive design, UI/UX implementation, SASS/LESS, Webpack, Babel, browser compatibility, DOM manipulation, CSS frameworks like Bootstrap and Tailwind, web accessibility, and frontend testing frameworks.",
    "backend": "Backend development involving server-side logic using Python, Node.js, Java, PHP, Ruby, Go, C#, REST/GraphQL APIs, database design and management (SQL, NoSQL), authentication/authorization, security practices, microservices architecture, middleware, caching, server management, message queues, web servers, frameworks like Django, Flask, Express, Spring, Laravel, and API documentation.",
    "full stack": "Full stack development combining both frontend and backend expertise, creating end-to-end applications, managing client-server architecture, implementing full application lifecycles, deploying full-stack solutions, integrating frontend and backend systems, working with JavaScript/TypeScript across the stack, full application debugging, RESTful service integration, and handling both UI/UX and database operations.",
    "ai": "Artificial intelligence development including natural language processing, computer vision, speech recognition, recommendation systems, reinforcement learning, generative AI, large language models, transformer architectures, knowledge graphs, AI ethics, neural networks (CNN, RNN, LSTM, GAN), prompt engineering, model optimization, AI system design, and AI application deployment.",
}


# Function to get text embedding from OpenAI
def get_embedding(text):
    time.sleep(12)
    response = client.embeddings.create(
        model="provider-3/text-embedding-ada-002", input=text
    )
    return response.data[0].embedding


# Cache these only once
reference_embeddings = {
    folder: get_embedding(text)
    for folder, text in folder_reference_map.items()
}

def get_best_matching_folder(job_description):
    job_embedding = get_embedding(job_description)

    best_folder = None
    best_score = -1.0

    for folder, folder_embedding in reference_embeddings.items():
        similarity = cosine_similarity([job_embedding], [folder_embedding])[0][0]
        print(f"{folder} → similarity: {similarity:.3f}")

        if similarity > best_score:
            best_folder = folder
            best_score = similarity

    return best_folder, best_score

@tool("match_and_process_jobs")
def match_and_process_jobs() -> str:
    """
    Reads a CSV file of job descriptions, matches each job to a folder from
    `folder_reference_map` using cosine similarity of OpenAI embeddings, and
    writes the matched folders to a new CSV file.
    """
    file_path = "linkedin_jobs.csv"
    if not os.path.exists(file_path):
        return f"❌ File not found at path: {file_path}"

    df = pd.read_csv(file_path)
    matched_folders = []
    processed_count = 0

    for idx, job_description in enumerate(df['job_description'].dropna(), 1):
        print(f"\n--- Job {idx} ---")
        best_folder, score = get_best_matching_folder(job_description)
        print(f"✅ Best match: {best_folder.upper()} (score: {score:.3f})")

        matched_folders.append(best_folder.upper())
        processed_count += 1
        time.sleep(10)

    # Add matched folder column to DataFrame
    df = df.loc[df['job_description'].notna()].copy()
    df["matched_folder"] = matched_folders

    # Save updated DataFrame to a new file
    output_path = file_path.replace(".csv", "_with_matches.csv")
    df.to_csv(output_path, index=False)
    # os.remove("linkedin_jobs.csv")

    return f"✅ Processed {processed_count} job descriptions successfully.\n📄 Output saved to: {output_path}"
