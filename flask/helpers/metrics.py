import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics import f1_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from helpers.KeySkillsChainApi import evaluate_resume_to_job
def compute_cosine_similarity(doc1, doc2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]

def compute_bleu_score(reference, hypothesis):
    # Tokenize reference and hypothesis
    reference_tokens = [reference.split()]  # BLEU expects a list of token lists
    hypothesis_tokens = hypothesis.split()

    # Apply BLEU with 2-gram order and smoothing
    bleu_score = sentence_bleu(
        reference_tokens, hypothesis_tokens, 
        weights=(0.5, 0.5),  # Weights for unigram and bigram only
        smoothing_function=SmoothingFunction().method1  # Apply smoothing
    )
    return bleu_score
# Function to compute F1 Score
def compute_f1_score(reference, candidate):
    # Convert to binary (1 for the words in common, 0 otherwise)
    reference_words = set(reference.split())
    candidate_words = set(candidate.split())
    
    true_positive = len(reference_words.intersection(candidate_words))
    precision = true_positive / len(candidate_words) if candidate_words else 0
    recall = true_positive / len(reference_words) if reference_words else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    return f1
def get_stat_average(jsonl_file):
    with open(jsonl_file, 'r') as file:
        original_bleu, original_cosine, original_f1 = 0, 0, 0
        new_bleu, new_cosine, new_f1 = 0, 0, 0
        total = 0
        
        for entry in file:
            data = json.loads(entry)
            reference = json.dumps(data['description'])
            original =  json.dumps(data["input"])
            output =  json.dumps(data['output'])
            original_bleu += compute_bleu_score(reference, original)
            original_cosine += compute_cosine_similarity(reference, original)
            original_f1 += compute_f1_score(reference, original)
            
            new_bleu += compute_bleu_score(reference, output)
            new_cosine += compute_cosine_similarity(reference, output)
            new_f1 += compute_f1_score(reference, output)
            
            total += 1
        
        if total == 0:
            return "No data to process."
        
        bleu_og_average = original_bleu / total
        f1_og_avg = original_f1 / total
        cosine_og_avg = original_cosine / total

        bleu_new_avg = new_bleu / total
        f1_new_avg = new_f1 / total
        cosine_new_avg = new_cosine / total

        summary = (
            f"Original Averages:\n"
            f"BLEU: {bleu_og_average:.2f}\n"
            f"Cosine Similarity: {cosine_og_avg:.2f}\n"
            f"F1 Score: {f1_og_avg:.2f}\n\n"
            f"New Averages:\n"
            f"BLEU: {bleu_new_avg:.2f}\n"
            f"Cosine Similarity: {cosine_new_avg:.2f}\n"
            f"F1 Score: {f1_new_avg:.2f}"
        )
        
        print(summary)

def get_llm_score(jsonl_file):
    count_one = 0
    count_two = 0
    total_entries = 0
    count_error = 0
    count_no_vote = 0

    with open(jsonl_file, 'r') as file:
        for entry in file:
            data = json.loads(entry)
            reference = json.dumps(data['description'])
            original = json.dumps(data["input"])
            output = json.dumps(data['output'])
            

            parsed_result = json.loads(evaluate_resume_to_job(reference, original, output))
            
            if parsed_result.get("choice") == "one":
                count_one += 1
            elif parsed_result.get("choice") == "two":
                count_two += 1
            elif parsed_result.get("choice") == "no vote":
                count_no_vote += 1
            else :
                count_error += 1
            total_entries += 1

    # Calculate percentages
    if total_entries > 0:
        percentage_one = (count_one / total_entries) * 100
        percentage_two = (count_two / total_entries) * 100
        percentage_error = (count_error / total_entries) * 100
        percentage_no_vote = (count_no_vote / total_entries) * 100
    else:
        percentage_one = 0
        percentage_two = 0
        percentage_error = 0
        percentage_error = 0

    # Print summary
    print(f"Total entries: {total_entries}")
    print(f"Number of 'one' choices: {count_one} ({percentage_one:.2f}%)")
    print(f"Number of 'two' choices: {count_two} ({percentage_two:.2f}%)")
    print(f"Number of 'no vote' choices: {count_no_vote} ({percentage_no_vote:.2f}%)")
    print(f"Number of 'error' choices: {count_error} ({percentage_error:.2f}%)")

def summarize_resume_metrics(cleaned_description, original_resume, updated_resume):
    # Compute metrics for original and updated resumes
    metrics = {
        "original": {
            "cosine": compute_cosine_similarity(cleaned_description, original_resume),
            "bleu": compute_bleu_score(cleaned_description, original_resume),
            "f1": compute_f1_score(cleaned_description, original_resume)
        },
        "updated": {
            "cosine": compute_cosine_similarity(cleaned_description, updated_resume),
            "bleu": compute_bleu_score(cleaned_description, updated_resume),
            "f1": compute_f1_score(cleaned_description, updated_resume)
        }
    }
    
    # Calculate deltas between updated and original metrics
    deltas = {
        "cosine": metrics["updated"]["cosine"] - metrics["original"]["cosine"],
        "bleu": metrics["updated"]["bleu"] - metrics["original"]["bleu"],
        "f1": metrics["updated"]["f1"] - metrics["original"]["f1"]
    }    # Display results
    print("---- Original Resume Metrics ----")
    print(f"Cosine Similarity: {metrics['original']['cosine']:.4f}")
    print(f"BLEU Score: {metrics['original']['bleu']:.4f}")
    print(f"F1 Score: {metrics['original']['f1']:.4f}")
    
    print("\n---- Updated Resume Metrics ----")
    print(f"Cosine Similarity: {metrics['updated']['cosine']:.4f}")
    print(f"BLEU Score: {metrics['updated']['bleu']:.4f}")
    print(f"F1 Score: {metrics['updated']['f1']:.4f}")
    
    print("\n---- Metric Changes (Delta) ----")
    print(f"Cosine Similarity Change: {deltas['cosine']:+.4f}")
    print(f"BLEU Score Change: {deltas['bleu']:+.4f}")
    print(f"F1 Score Change: {deltas['f1']:+.4f}")
    
    # Summary of improvement or regression
    summary = "improvement" if any(delta > 0 for delta in deltas.values()) else "regression"
    print(f"\nOverall Summary: {summary} in alignment with job description.")