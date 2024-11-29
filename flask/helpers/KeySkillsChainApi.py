import json
from helpers.LLMClient import LLMGetClient, LLMClientType
from dotenv import load_dotenv
import os
load_dotenv()
model_name = os.getenv("MODEL_NAME")
api_key = os.getenv("API_KEY")
model_type = os.getenv("MODEL_TYPE")
api_type = LLMClientType.HUGGINGFACE
if model_type == "openai":
    api_type = LLMClientType.OPENAI #api_type = LLMClientType.OPENAI
llm_client = LLMGetClient(api_type, api_key)


def extract_text_segment(text, start_token, end_token):
    start_index = text.find(start_token) + len(start_token)
    end_index = text.find(end_token, start_index)
    if start_index == -1 or end_index == -1:
        return text
    return text[start_index:end_index]

def fetch_job_skills(job_description ):
    template = f"""
    Job Description:
    {job_description}

    Please extract and list the top items from each category in JSON format. Avoid redundancy and provide no additional context:

    "Languages": [comma-separated list]
    "Technologies": [comma-separated list]
    "Frameworks": [comma-separated list]

    Verify valid json format

    """

    system_message = """
    You are a skilled language model designed to extract key skills from job descriptions. Your task is to identify and categorize skills into "Languages", "Technologies", and "Frameworks". Ensure each category is concise and relevant. If a category is not explicitly mentioned, infer the skills to the best of your ability without providing additional explanations.
    """
    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ] 
    output = llm_client.generate_output(model_name, messages)
    return output

def fetch_job_relevant_experience(job_description ):
    template = f"""
    Job Description:
    {job_description}

    Please extract and list the key components from the resume in JSON format, focusing on the most relevant items for each category. Avoid redundancy and do not provide additional context:

    "Technical Skills": [comma-separated list]
    "Professional Experience": [comma-separated list]
    "Educational Background": [comma-separated list]
    "Soft Skills": [comma-separated list]
    "Industry Knowledge": [comma-separated list]
    "Other Requirements": [comma-separated list]
    """

    system_message = """
    You are an advanced language model tasked with extracting key components from a resume based on a given job description. Your objective is to categorize experiences into "Technical Skills," "Professional Experience," "Educational Background," "Soft Skills," "Industry Knowledge," and "Other Requirements." Ensure that each category is concise and relevant to the job description. If a category is not explicitly mentioned, infer the key components to the best of your ability, without adding any extra explanations
    """

    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = llm_client.generate_output(model_name, messages)
    return output

def align_experience_with_job( extracted_experience, resume_experiences ):
    template = f"""
    Extracted Key Experiences:
    {extracted_experience}

    Resume Bullet Points:
    {resume_experiences}
    """
    system_message = """
    You are an expert language model tasked with updating only the "experience" section of a resume based on key skills and experiences extracted from job descriptions. Each bullet point should be relevant, impactful, and clearly reflect the skills and experiences described in the key experiences. Ensure that each bullet point highlights specific achievements, quantifiable results, and the direct impact of the candidate's contributions. Emphasize the diversity of technologies and frameworks used, and ensure that the updated experience section demonstrates a broad and varied skill set. Output the revised "experience" section in JSON format, with no additional explanations. Do not change the structure, order, or formatting of the JSON. Only update the text within the existing structure. Do not add any additional text or comments. Ensure the JSON is valid and properly formatted.
    """
    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = llm_client.generate_output(model_name, messages)
    return output

def align_projects_with_job(extracted_experience, resume_projects ):
    template = f"""
    Extracted Key Experiences:
    {extracted_experience}

    Resume Bullet Points:
    {resume_projects}
    """

    system_message = """
        You are an expert language model tasked with updating only the "projects" section of a resume based on key skills and experiences extracted from job descriptions. Each bullet point should be relevant, impactful, and clearly reflect the skills and experiences described in the key experiences. Ensure that each bullet point highlights specific achievements, quantifiable results, and the direct impact of the candidate's contributions. Emphasize the diversity of technologies and frameworks used, and ensure that the updated experience section demonstrates a broad and varied skill set. Output the revised "projects" section in JSON format, with no additional explanations. Do not change the structure, order, or formatting of the JSON. Only update the text within the existing structure. Do not add any additional text or comments. Ensure the JSON is valid and properly formatted.
    """


    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = llm_client.generate_output(model_name, messages)
    return output

def merge_skills(existing_skills, new_skills):
    try:
        languages_set = set(existing_skills["skills"]["languages:"].split(", "))
    except KeyError:
        languages_set = set()

    try:
        technologies_set = set(existing_skills["skills"]["technologies:"].split(", "))
    except KeyError:
        technologies_set = set()

    try:
        frameworks_set = set(existing_skills["skills"]["frameworks:"].split(", "))
    except KeyError:
        frameworks_set = set()
    # Add new skills to the respective sets
    languages_set.update(new_skills['Languages'])
    technologies_set.update(new_skills['Technologies'])
    frameworks_set.update(new_skills['Frameworks'])

    # Convert the sets back to sorted, comma-separated strings
    combined_skills = {
        "skills": {
            "languages:": ", ".join(sorted(languages_set)),
            "technologies:": ", ".join(sorted(technologies_set)),
            "frameworks:": ", ".join(sorted(frameworks_set))
        }
    }
    return combined_skills

def generate_resume_update(job_description, resume_data):
    parsed_resume = json.loads(resume_data)
    experience_section = json.dumps({"experience": parsed_resume.get("experience", {})})
    project_section = json.dumps({"projects": parsed_resume.get("projects", {})})
    education_section = {"education": parsed_resume.get("education", {})}

    skill_data_str = fetch_job_skills(job_description)
    extracted_skills = json.loads(extract_text_segment(skill_data_str, "```json", "```"))
    combined_skills = merge_skills(parsed_resume, extracted_skills)
    print("\n\nExtracted Job Skills")

    job_experience_str = fetch_job_relevant_experience(job_description)
    extracted_experience = extract_text_segment(job_experience_str, "```json", "```")

    print("\n\nExtracted Job Experience")
    aligned_experience = align_experience_with_job(extracted_experience, experience_section)
    aligned_experience_json = json.loads(extract_text_segment(aligned_experience, "```json", "```"))
    if not isinstance(aligned_experience_json, dict) or 'experience' not in map(str.lower, aligned_experience_json.keys()):
        aligned_experience_json = {"experience": aligned_experience_json}
    aligned_experience_json = {k.lower(): v for k, v in aligned_experience_json.items()}

    print("\n\nExtracted Aligned Experience")
    aligned_projects = align_projects_with_job(extracted_experience, project_section)
    aligned_projects_json = json.loads(extract_text_segment(aligned_projects, "```json", "```"))
    if not isinstance(aligned_projects_json, dict) or 'projects' not in map(str.lower, aligned_projects_json.keys()):
        aligned_projects_json = {"projects": aligned_projects_json}
    aligned_projects_json = {k.lower(): v for k, v in aligned_projects_json.items()}

    final_resume = {
        **combined_skills,
        **aligned_experience_json,
        **aligned_projects_json,
        **education_section,
    }
    return json.dumps(final_resume, indent=4), extracted_experience

def update_resume_with_query(resume_content, update_query):
    template = f"""
    Resume:
    {resume_content}

    Query:
    {update_query}
    """

    system_message = """
    You are an AI assistant that helps users update their resumes. You will receive a resume in JSON format and a query specifying the updates needed. Your task is to apply the updates to the resume and return the updated resume in the same JSON format. 
    Do not change the structure or formatting of the JSON. Only update the text as specified in the query. Do not add any additional text or comments.    """

    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = llm_client.generate_output(model_name, messages)
    output = extract_text_segment(output, "```json", "```")
    return output

def parse_evaluation_output(output):
    try:
        stats = json.loads(output)
        return stats
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON output: {e}"}

def evaluate_resume_to_job(job_description, original, updated):
    template = f"""
    Resume One:
    {original}

    Resume Two:
    {updated}

    Job Description:
    {job_description}
    """

    system_message = """
    You are an AI assistant that evaluates resumes against a job description. You will receive a job description and two resumes. Your task is to compare the resumes and determine which one is a better fit for the job description. Output the result in the following JSON format:
    
    {
        "choice": "one", "two", or "no vote",
        "explanation": "Brief explanation of why the chosen resume is a better fit."
    }
    """

    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]

    output = llm_client.generate_output(model_name, messages)
    return extract_text_segment(json.dumps(parse_evaluation_output(output)), "```json", "```") 