from werkzeug.utils import secure_filename
from helpers.utility import allowed_file, append_llm_output
from helpers.KeySkillsChainApi import execute_prompt
from helpers.metrics import summarize_resume_metrics
from helpers.ResumeParser import ResumeParser
from helpers.WordcCompare import compare_strings, generate_html_diff
from flask import Flask, request, redirect, url_for, render_template, session
import os
import re
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'docx'}
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.config["OUTPUT_PATH"] = 'outputs/output.jsonl'


def load_jobs():
    with open('jobs.json') as f:
        jobs = json.load(f)
        return jobs
pages = [
        {"name": "Home", "url": "/"},
        {"name": "Jobs", "url": "/jobs"},
        # Add more pages as needed
]

@app.route('/jobs')
def job_list():
    jobs = load_jobs()
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
    resume_path = session.get('resume-path')  # Retrieve job data from session

    parser = ResumeParser(resume_path)
    parser.parse()
    resume_str = parser.as_str()

    # Convert job data to JSON string
    job_data = request.get_json()
    description = json.loads(job_data['data'])['description']
    cleaned_description = re.sub(r'[^A-Za-z0-9 ]+', '', description.replace('\n', ' '))
    prompt_out = execute_prompt(job_description=cleaned_description, user_skills=resume_str)
    output_data = json.loads(prompt_out)
    input_data = json.loads(resume_str)

    # Combine into a new dictionary with "output" and "input" headers
    combined_data = {
        "output": output_data,
        "input": input_data
    }
    summarize_resume_metrics(cleaned_description, resume_str, prompt_out)
    append_llm_output(app.config["OUTPUT_PATH"], json.dumps(combined_data, indent=4))
    return redirect(url_for('compare', original=resume_str, new=prompt_out))

@app.route('/compare')
def compare():
    original = request.args.get('original')
    new = request.args.get('new')

    diff = compare_strings(original, new)
    original_html, new_html = generate_html_diff(diff)
    return render_template('compare.html', original=original_html, new=new_html)



@app.route('/')
def index():
    return render_template('index.html', pages=pages)

@app.route('/uploadV2', methods=['POST'])
def upload_filev2():
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
