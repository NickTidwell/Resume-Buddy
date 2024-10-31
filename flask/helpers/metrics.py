import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics import f1_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

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