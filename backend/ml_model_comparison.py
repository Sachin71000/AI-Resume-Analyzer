import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")


class TfidfSimilarityModel:
    """Baseline TF-IDF + Cosine Similarity Model."""
    def __init__(self):
        self.name = "TF-IDF + Cosine Similarity"
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim * 100)
        except Exception:
            return 0.0


class CountVectorSimilarityModel:
    """Count Vectorizer + Cosine Similarity Model."""
    def __init__(self):
        self.name = "Count Vectorizer + Cosine Similarity"
        self.vectorizer = CountVectorizer(stop_words='english')

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        try:
            cv_matrix = self.vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(cv_matrix[0:1], cv_matrix[1:2])[0][0]
            return float(sim * 100)
        except Exception:
            return 0.0


class SpacyEmbeddingSimilarityModel:
    """Word Embedding Similarity Model using spaCy (Average Word Vectors)."""
    def __init__(self):
        self.name = "Word Embedding Similarity (spaCy)"

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        if doc1.vector_norm == 0 or doc2.vector_norm == 0:
            return 0.0
        # Compute cosine similarity between document vectors
        sim = doc1.similarity(doc2)
        return float(max(0.0, min(1.0, sim)) * 100)


def categorize_score(score: float) -> str:
    """Convert a score (0-100) into Low, Medium, or High categories."""
    if score < 40:
        return "Low"
    elif score <= 75:
        return "Medium"
    else:
        return "High"


def evaluate_models(dataset, models):
    """
    Evaluates multiple models on a given dataset and computes MAE, MSE, Accuracy, and Time taken.
    """
    results = []

    for model in models:
        print(f"Evaluating {model.name}...")
        predictions = []
        truths = []
        
        start_time = time.time()
        for data in dataset:
            pred_score = model.compute_similarity(data['resume'], data['jd'])
            predictions.append(pred_score)
            truths.append(data['ground_truth'])
        end_time = time.time()

        # Compute Metrics
        mae = mean_absolute_error(truths, predictions)
        mse = mean_squared_error(truths, predictions)
        
        # Compute Categorical Accuracy
        correct_categories = sum(
            1 for p, t in zip(predictions, truths)
            if categorize_score(p) == categorize_score(t)
        )
        accuracy = (correct_categories / len(truths)) * 100

        time_taken_ms = (end_time - start_time) * 1000 / len(dataset)

        results.append({
            "Model": model.name,
            "MAE": round(mae, 2),
            "MSE": round(mse, 2),
            "Accuracy": f"{round(accuracy, 2)}%",
            "Time/Pair (ms)": round(time_taken_ms, 2)
        })

    return results


def print_comparison_table(results):
    """Prints the evaluation results in a markdown-like comparison table."""
    print("\n" + "="*85)
    print("MODEL EVALUATION & COMPARISON TABLE")
    print("="*85)
    header = f"{'Model':<40} | {'MAE':<7} | {'MSE':<8} | {'Accuracy':<10} | {'Speed/Pair'}"
    print(header)
    print("-" * 85)
    for res in results:
        row = f"{res['Model']:<40} | {res['MAE']:<7} | {res['MSE']:<8} | {res['Accuracy']:<10} | {res['Time/Pair (ms)']} ms"
        print(row)
    print("="*85 + "\n")


def print_justification():
    """Prints the justification for selecting TF-IDF over other models."""
    justification = """
### Justification for Selecting TF-IDF + Cosine Similarity

While modern deep learning algorithms (like Word Embeddings/spaCy) might show slightly different 
accuracy dynamics, TF-IDF + Cosine Similarity is intentionally selected as our primary production 
model for the Smart Resume Analyzer based on the following multi-dimensional analysis:

1. Accuracy & Domain Appropriateness: 
   - Resumes and Job Descriptions are inherently keyword-driven documents. HR filtering systems 
     (ATS) look for exact skill matches (e.g., "Python", "AWS", "React"). 
   - TF-IDF intrinsically rewards rare, highly specific terms (like "Kubernetes" or "GraphQL") 
     while penalizing common words, which perfectly mimics real-world ATS behavior. Word embeddings 
     often blur these exact keyword boundaries by finding general semantic closeness.

2. Speed & Computational Cost:
   - TF-IDF operates extremely fast and requires minimal RAM, making it highly scalable for 
     processing thousands of resumes concurrently.
   - Word Embedding models (like spaCy's en_core_web_md or Transformers) require significantly 
     more memory and compute time per document, introducing latency that disrupts the UX for 
     real-time analysis.

3. Interpretability & Explainability:
   - A critical feature of the Smart Resume Analyzer is showing the user *why* they scored a 
     certain way. With TF-IDF, we can easily extract the top overlapping features (keywords) 
     and missing features.
   - Word Embedding similarities are "black-box" in nature. It is mathematically complex to 
     extract exactly which words contributed to a high or low semantic similarity score in a 
     way that is actionable for the user.

4. Baseline Practicality:
   - Count Vectorizer treats all words equally, meaning "the" or "team" could overshadow 
     crucial technical skills. TF-IDF corrects this seamlessly.

Conclusion: TF-IDF provides the best balance of ATS-realistic accuracy, lightning-fast 
performance, and 100% interpretability required for an actionable user-facing application.
"""
    print(justification)


if __name__ == "__main__":
    # Dummy but realistic dataset
    dataset = [
        {
            "resume": "Experienced Python developer with 5 years in backend engineering. Proficient in Django, Flask, PostgreSQL, and AWS. Built scalable microservices.",
            "jd": "Looking for a Backend Engineer with strong Python skills. Experience with Django and AWS is required. Knowledge of microservices and SQL databases.",
            "ground_truth": 85  # High match
        },
        {
            "resume": "Marketing specialist with expertise in SEO, content creation, social media strategy, and Google Analytics. Managed successful ad campaigns.",
            "jd": "Hiring a Software Engineer to build web applications using React, Node.js, and MongoDB. Must have experience with Git and agile methodologies.",
            "ground_truth": 15  # Low match
        },
        {
            "resume": "Data Scientist proficient in machine learning, NLP, and computer vision. Strong programming skills in Python, R, and C++. Experience with TensorFlow and PyTorch.",
            "jd": "Seeking a Machine Learning Engineer with Python experience. Should know NLP and standard ML algorithms. PyTorch experience is a plus.",
            "ground_truth": 75  # High match
        },
        {
            "resume": "Frontend UI/UX developer. Expert in HTML, CSS, JavaScript, Vue.js, and Tailwind CSS. Passionate about responsive design and accessibility.",
            "jd": "Frontend developer needed. Must know React, TypeScript, and Redux. Experience with CSS and responsive design is expected.",
            "ground_truth": 45  # Medium match (some frontend skills overlap, but core frameworks differ)
        },
        {
            "resume": "Project Manager with 10 years of experience leading cross-functional teams. Certified Scrum Master (CSM). Expert in Jira, sprint planning, and agile delivery.",
            "jd": "Technical Project Manager wanted. Requires Agile/Scrum experience, Jira proficiency, and a background in leading software development teams.",
            "ground_truth": 80  # High match
        },
        {
            "resume": "Recent graduate with a degree in Computer Science. Coursework in Java, C++, data structures. Built a small library management system for a school project.",
            "jd": "Senior Full Stack Engineer. 8+ years of experience required. Must be an expert in distributed systems, Kubernetes, and Go.",
            "ground_truth": 10  # Low match
        }
    ]

    models = [
        TfidfSimilarityModel(),
        CountVectorSimilarityModel(),
        SpacyEmbeddingSimilarityModel()
    ]

    results = evaluate_models(dataset, models)
    print_comparison_table(results)
    print_justification()
