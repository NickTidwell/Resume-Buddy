# Resume Buddy

Resume Buddy is a project aimed at enhancing resumes using Large Language Models (LLMs) to align with job descriptions. This repository includes tools for resume processing, job scraping, and metrics generation.

---

## Project Structure

### Dataset
- **Static Outputs**: Contains predefined results for testing and verification.
- **Contents**:
  - `sample-outputs`: Results from 60 test runs.
  - `sample-resumes`: Example resumes used for testing.
  - `jobs.json`: Job data used during testing.

### Flask
- **Backend and Frontend Hosting**:
  - To run the application:
    ```bash
    python app.py
    ```
    The app defaults to `http://localhost:5000`.
- **Key Components**:
  - `templates/`: Contains frontend HTML files.
  - `helpers/`: Python utilities for LLM processing.
  - `get_metrics.py`: Processes output metrics automatically and saves results in the `/outputs` folder.

### JobScraper
- **LinkedIn Job Scraping Tools**:
  - Requires a running Chrome instance and LinkedIn login.
  - **Main Script**:
    - `LinkedInJobScraper.py`: Takes in a query and scrapes job postings based on the specified parameters.

---

## Configuration

### Requirements
- `requirements.txt`: Contains the list of Python dependencies for the current test environment. This file can be optimized in the future to remove unused dependencies.

### Environment Variables
- The `.env` file specifies the LLM configurations required to run the project.

#### Example 1: Hugging Face Model Configuration
```env
MODEL_TYPE=hf
MODEL_NAME=microsoft/Phi-3.5-mini-instruct
API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
#### Example 2:: OpenAI Model Configuration
```env
MODEL_TYPE=openai
MODEL_NAME=gpt-4o-mini
API_KEY=sk-proj-XX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXX
```

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd resume-buddy
2. **Install Dependencies**:
   ```bash
    pip install -r requirements.txt
    ```
3. **Set Up Environment Variables**:
    Create a .env file in the root directory.
    Configure it with your desired LLM settings (e.g., MODEL_TYPE, MODEL_NAME, and API_KEY).
4. **Run the Flask Application:**
   ```bash
    python app.py
    ```