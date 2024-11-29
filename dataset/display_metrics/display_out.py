import pandas as pd

# Data for each profession
data = [
    {"Profession": "Physical Therapist", "BLEU_Original": 0.01, "Cosine_Original": 0.22, "F1_Original": 0.09,
     "BLEU_New": 0.04, "Cosine_New": 0.27, "F1_New": 0.11},
    {"Profession": "Nurse", "BLEU_Original": 0.02, "Cosine_Original": 0.29, "F1_Original": 0.09,
     "BLEU_New": 0.05, "Cosine_New": 0.39, "F1_New": 0.13},
    {"Profession": "Finance Analyst", "BLEU_Original": 0.01, "Cosine_Original": 0.11, "F1_Original": 0.06,
     "BLEU_New": 0.05, "Cosine_New": 0.43, "F1_New": 0.15},
    {"Profession": "Software Engineer", "BLEU_Original": 0.02, "Cosine_Original": 0.24, "F1_Original": 0.07,
     "BLEU_New": 0.03, "Cosine_New": 0.29, "F1_New": 0.09},
    {"Profession": "Graphic Designer", "BLEU_Original": 0.02, "Cosine_Original": 0.16, "F1_Original": 0.08,
     "BLEU_New": 0.04, "Cosine_New": 0.39, "F1_New": 0.13},
    {"Profession": "Teacher", "BLEU_Original": 0.01, "Cosine_Original": 0.22, "F1_Original": 0.06,
     "BLEU_New": 0.02, "Cosine_New": 0.33, "F1_New": 0.09},
]

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Calculate combined averages
combined_averages = {
    "Profession": "Combined Average",
    "BLEU_Original": df["BLEU_Original"].mean(),
    "Cosine_Original": df["Cosine_Original"].mean(),
    "F1_Original": df["F1_Original"].mean(),
    "BLEU_New": df["BLEU_New"].mean(),
    "Cosine_New": df["Cosine_New"].mean(),
    "F1_New": df["F1_New"].mean()
}

# Append combined averages to the DataFrame
df = pd.concat([df, pd.DataFrame([combined_averages])], ignore_index=True)

# Display the table
print(df)


import pandas as pd

# Define data for each profession
data = [
    {"Profession": "Physical Therapist", "Total Entries": 10, "One Choices": 0, "One %": "0.00%", "Two Choices": 8, "Two %": "80.00%", "No Vote Choices": 2, "No Vote %": "20.00%"},
    {"Profession": "Nurse", "Total Entries": 10, "One Choices": 0, "One %": "0.00%", "Two Choices": 10, "Two %": "100.00%", "No Vote Choices": 0, "No Vote %": "0.00%"},
    {"Profession": "Finance Analyst", "Total Entries": 10, "One Choices": 0, "One %": "0.00%", "Two Choices": 10, "Two %": "100.00%", "No Vote Choices": 0, "No Vote %": "0.00%"},
    {"Profession": "Software Engineer", "Total Entries": 10, "One Choices": 1, "One %": "10.00%", "Two Choices": 7, "Two %": "70.00%", "No Vote Choices": 2, "No Vote %": "20.00%"},
    {"Profession": "Graphic Designer", "Total Entries": 10, "One Choices": 0, "One %": "0.00%", "Two Choices": 10, "Two %": "100.00%", "No Vote Choices": 0, "No Vote %": "0.00%"},
    {"Profession": "Teacher", "Total Entries": 10, "One Choices": 0, "One %": "0.00%", "Two Choices": 9, "Two %": "90.00%", "No Vote Choices": 1, "No Vote %": "10.00%"}
]

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)
