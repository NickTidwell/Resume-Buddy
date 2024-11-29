import pandas as pd

# Job data as a list of dictionaries
jobs = [
    {"job_title": "Software Engineer", "retrieved_10": 6, "relevant_10": 10, "retrieved_5": 5, "relevant_5": 5},
    {"job_title": "Physical Therapist", "retrieved_10": 5, "relevant_10": 10, "retrieved_5": 2, "relevant_5": 5},
    {"job_title": "Nurse", "retrieved_10": 6, "relevant_10": 10, "retrieved_5": 5, "relevant_5": 5},
    {"job_title": "Teacher", "retrieved_10": 10, "relevant_10": 10, "retrieved_5": 5, "relevant_5": 5},
    {"job_title": "Finance Analyst", "retrieved_10": 5, "relevant_10": 10, "retrieved_5": 3, "relevant_5": 5},
    {"job_title": "Graphic Designer", "retrieved_10": 9, "relevant_10": 10, "retrieved_5": 5, "relevant_5": 5}
]

# Variables to accumulate precision values for combined precision calculation
total_precision_10 = 0
total_precision_5 = 0
total_jobs = len(jobs)

# Create a list to store the results
results = []

for job in jobs:
    # Calculate precision@10 and precision@5
    precision_10 = job["retrieved_10"] / 10
    precision_5 = job["retrieved_5"] / 5
    
    # Accumulate values for combined precision
    total_precision_10 += precision_10
    total_precision_5 += precision_5
    
    # Add the job and precision values to the results list
    results.append({
        "Job Title": job["job_title"],
        "Precision@10": f"{precision_10:.2f}",
        "Precision@5": f"{precision_5:.2f}"
    })

# Calculate and display combined precision
combined_precision_10 = total_precision_10 / total_jobs
combined_precision_5 = total_precision_5 / total_jobs

# Add combined precision as a row
results.append({
    "Job Title": "Combined Precision",
    "Precision@10": f"{combined_precision_10:.2f}",
    "Precision@5": f"{combined_precision_5:.2f}"
})

# Convert the results into a pandas DataFrame
df = pd.DataFrame(results)

# Display the table
print(df)
