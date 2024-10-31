import json
from helpers.LLMClient import LLMGetClient, LLMClientType
from dotenv import load_dotenv
import os
load_dotenv()
model_name = os.getenv("MODEL_NAME")
api_key = os.getenv("API_KEY")
api_type = LLMClientType.HUGGINGFACE #api_type = LLMClientType.OPENAI
client = LLMGetClient(api_type, api_key)


def extract_between(text, start_token, end_token):
    start_index = text.find(start_token) + len(start_token)
    end_index = text.find(end_token, start_index)
    if start_index == -1 or end_index == -1:
        return text
    return text[start_index:end_index]

def extract_job_skills(job_description ):
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
    output = client.generate_output(model_name, messages)
    return output

def extract_job_experiences(job_description ):
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
        You are an advanced language model tasked with extracting key components from a resume based on a given job description. Your objective is to categorize experiences into "Technical Skills," "Professional Experience," "Educational Background," "Soft Skills," "Industry Knowledge," and "Other Requirements." Ensure that each category is concise and relevant to the job description. If a category is not explicitly mentioned, infer the key components to the best of your ability, without adding any extra explanations.
        """

    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = client.generate_output(model_name, messages)
    return output

def extract_aligned_experiences(extracted_key_experiences, resume_bullet_points ):
    template = f"""
    Extracted Key Experiences:
    {extracted_key_experiences}

    Resume Bullet Points:
    {resume_bullet_points}
    """
    system_message = """
    You are an expert language model tasked with updating only the "experience" section of a resume based on key skills and experiences extracted from job descriptions. Each bullet point should be relevant, impactful, and clearly reflect the skills and experiences described in the key experiences. Output the revised "experience" section in JSON format, with no additional explanations, and keep Resume Bullet Points formatting.
    """

    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = client.generate_output(model_name, messages)
    return output

def extract_projects_experiences(extracted_key_experiences, resume_bullet_points ):
    template = f"""
    Extracted Key Experiences:
    {extracted_key_experiences}

    Resume Bullet Points:
    {resume_bullet_points}
    """

    system_message = """
    You are an expert language model tasked with updating only the "projects" section of a resume based on key skills and experiences extracted from job descriptions. Each bullet point should be relevant, impactful, and clearly reflect the skills and experiences described in the key experiences. Output the revised "projects" section in JSON format, with no additional explanations, and keep Resume Bullet Points formatting.
    """


    messages = [ 
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": template}, 
    ]
    output = client.generate_output(model_name, messages)
    return output

def combine_skills(existing_skills, new_skills):
    languages_set = set(existing_skills["skills"]["languages:"].split(", "))
    technologies_set = set(existing_skills["skills"]["technologies:"].split(", "))
    frameworks_set = set(existing_skills["skills"]["frameworks:"].split(", "))
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

def execute_prompt(job_description, user_skills):
    usr_json = json.loads(user_skills)
    experiences =  json.dumps({"experience": usr_json.get("experience", {})})
    user_projects = json.dumps({"projects": usr_json.get("projects", {})})
    user_education_json = {"education": usr_json.get("education", {})}

    desc_skills_str = extract_job_skills(job_description)
    extracted_desc = extract_between(desc_skills_str, "```json", "```")
    new_json = json.loads(extracted_desc)
    new_skills_json = combine_skills(usr_json, new_json)

    print("\n\nExtracted Job Skills")

    job_experiencs_json = extract_job_experiences(job_description)
    extracted_experiences = extract_between(job_experiencs_json, "```json", "```")
    print("\n\nExtracted Job Experience")

    align_experience_out = extract_aligned_experiences(extracted_experiences, experiences)
    align_experience_json = extract_between(align_experience_out, "```json", "```")
    align_experience_json = json.loads(align_experience_json)
    if not isinstance(align_experience_json, dict) or 'experience' not in map(str.lower, align_experience_json.keys()):
        align_experience_json = {"experience": align_experience_json}
    align_experience_json = {k.lower(): v for k, v in align_experience_json.items()}
    print("\n\nExtracted Aligned Experience")


    align_projects_out = extract_projects_experiences(extracted_experiences, user_projects)
    align_projects_json = extract_between(align_projects_out, "```json", "```")
    align_projects_json = json.loads(align_projects_json)
    if not isinstance(align_projects_json, dict) or 'projects' not in map(str.lower, align_projects_json.keys()):
        align_projects_json = {"projects": align_projects_json}
    align_projects_json = {k.lower(): v for k, v in align_projects_json.items()}

    combined_json = {**new_skills_json, **align_experience_json, **align_projects_json, **user_education_json}
    combined_str = json.dumps(combined_json, indent=4)
    return combined_str
