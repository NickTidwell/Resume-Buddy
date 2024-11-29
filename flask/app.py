from werkzeug.utils import secure_filename
from helpers.utility import allowed_file, append_llm_output
from helpers.KeySkillsChainApi import generate_resume_update, update_resume_with_query
from helpers.metrics import summarize_resume_metrics
from helpers.ResumeParser import ResumeParser
from helpers.WordCompare import compare_strings, generate_html_diff
from flask import Flask, request, redirect, url_for, render_template, session
import os
import re
import json
from langchain_community.document_loaders import JSONLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'docx'}
app.config["OUTPUT_PATH"] = 'outputs/output.jsonl'
app.secret_key = 'SUPER_SECRET'

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
loader = JSONLoader(file_path="./jobs.json", jq_schema=".jobs[].description", text_content=False)
documents = loader.load()
db = Chroma.from_documents(documents, embedding_function)

def load_jobs():
    with open('jobs.json') as f:
        jobs = json.load(f)['jobs']
        return jobs, db

pages = [
    {"name": "Home", "url": "/"},
    {"name": "Jobs", "url": "/jobs"},
]
@app.route('/jobs')
def job_list():
    jobs, db = load_jobs()
    resume_path = session.get('resume-path')
    parser = ResumeParser(resume_path)
    parser.parse()
    resume_str = parser.as_str()
    docs = db.similarity_search(f"Select the best jobs for the candidate resume: {resume_str}. Focus on job titles, career progression, and relevant experience.", k=5)
    itr = 0
    for doc in docs:
        index = doc.metadata['seq_num'] - 1
        jobs[index]['recommended'] = 1
        itr += 1
    # Second pass: Move recommended jobs to the top of the list
    recommended_jobs = [job for job in jobs if job.get('recommended') == 1]
    non_recommended_jobs = [job for job in jobs if job.get('recommended') != 1]

    # Combine the lists with recommended jobs at the top
    jobs = recommended_jobs + non_recommended_jobs
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total = len(jobs)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_jobs = jobs[start:end]
    return render_template('jobs.html', jobs=paginated_jobs, page=page, total=total, per_page=per_page, pages=pages)

@app.route('/select_job', methods=['POST'])
def job_selected():
    job_data = request.get_json()
    job_data_str = json.dumps(job_data)  # Convert job data to JSON string
    return redirect(url_for('align', job_data=job_data_str))

@app.route('/align-check')
def align():
    job_data_str = request.args.get('job_data')
    job_data = json.loads(job_data_str)  # Convert JSON string back to dictionary
    resume_path = session.get('resume-path')  # Retrieve job data from session
    resume_name = os.path.basename(resume_path)
    return render_template('align-check.html', job_data=job_data, resume=resume_name)

@app.route('/align-skills', methods=['POST'])
def align_skills():
    resume_path = session.get('resume-path')
    parser = ResumeParser(resume_path)
    parser.parse()
    resume_str = parser.as_str()

    job_data = request.get_json()
    description = json.loads(job_data['data'])['description']
    cleaned_description = re.sub(r'[^A-Za-z0-9 ]+', '', description.replace('\n', ' '))
    
    prompt_out, desc_summary = generate_resume_update(job_description=cleaned_description, resume_data=resume_str)
    output_data = json.loads(prompt_out)
    input_data = json.loads(resume_str)
    combined_data = {
        "output": output_data,
        "input": input_data,
        "description": desc_summary
    }
    
    summarize_resume_metrics(cleaned_description, resume_str, prompt_out)
    append_llm_output(app.config["OUTPUT_PATH"], json.dumps(combined_data))
    return redirect(url_for('compare', original=resume_str, new=prompt_out))

@app.route('/compare')
def compare():
    original = request.args.get('original')
    new = request.args.get('new')

    diff = compare_strings(original, new)
    original_html, new_html = generate_html_diff(diff)
    return render_template('compare.html', original=original_html, new=new_html)


@app.route('/update', methods=['POST'])
def update():
    query = request.form.get('update-query')
    new_html = request.form.get('new-html')

    resume_path = session.get('resume-path')  # Retrieve job data from session
    parser = ResumeParser(resume_path)
    parser.parse()
    resume_str = parser.as_str()

    updated_output = update_resume_with_query(new_html, query)
    updated_output = json.loads(updated_output)
    updated_output = json.dumps(updated_output, indent=4)
    # Redirect back to the compare page with the updated new_html
    return redirect(url_for('compare', original=resume_str, new=updated_output))
@app.route('/')
def index():
    return render_template('index.html', pages=pages)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return 'No file part'
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return 'No selected file'
    if resume_file and allowed_file(resume_file.filename, app.config['ALLOWED_EXTENSIONS']):
        secureresume_file = secure_filename(resume_file.filename)
        file_location = f"{app.config['UPLOAD_FOLDER']}/{secureresume_file}"
        resume_file.save(file_location)
        session['resume-path'] = file_location  # Store job data in session
        return redirect(url_for('job_list'))


if __name__ == '__main__':
    app.run()
