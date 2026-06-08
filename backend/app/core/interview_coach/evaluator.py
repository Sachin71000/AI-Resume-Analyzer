import re
import logging
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ...services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class GeminiEvaluationSchema(BaseModel):
    correctness: int = Field(ge=0, le=10, description="Factual correctness of the answer, out of 10.")
    completeness: int = Field(ge=0, le=10, description="Completeness in addressing all parts of the question, out of 10.")
    clarity: int = Field(ge=0, le=10, description="Clarity, articulation, and structure of the response, out of 10.")
    depth: int = Field(ge=0, le=10, description="Technical depth and understanding demonstrated, out of 10.")
    overall: float = Field(ge=0.0, le=10.0, description="Overall weighted score representing the quality of the answer, out of 10.")
    strengths: list[str] = Field(description="Specific points or concepts the candidate got right (1-3 bullets).")
    weaknesses: list[str] = Field(description="Specific points, details, or nuances the candidate missed or got wrong (1-3 bullets).")
    improvement_tip: str = Field(description="One specific, actionable advice to make this answer significantly better.")

class Evaluator:
    # 3-Layer Weighted Scores
    WEIGHT_TFIDF = 0.25
    WEIGHT_KEYWORD = 0.25
    WEIGHT_GEMINI = 0.50

    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service

    def evaluate_answer(
        self,
        question_text: str,
        user_answer: str,
        ideal_answer: str,
        keywords: list[str]
    ) -> dict:
        """
        Runs the 3-layer evaluation pipeline:
        - Layer 1: TF-IDF cosine similarity with ideal answer (25%)
        - Layer 2: Keyword matching (25%)
        - Layer 3: Gemini Semantic grading (50%)
        """
        # Clean answer
        user_answer_clean = user_answer.strip()
        
        # Guard for empty answers
        if not user_answer_clean:
            return {
                "score": 0.0,
                "tfidf_score": 0.0,
                "keyword_score": 0.0,
                "gemini_score": 0.0,
                "verdict": "Unanswered",
                "strengths": [],
                "weaknesses": ["No answer was provided."],
                "improvement_tip": "Make sure to write or speak an answer to receive credit.",
                "keywords_found": [],
                "metrics": {
                    "word_count": 0,
                    "filler_word_count": 0,
                    "technical_depth_score": 0.0
                }
            }

        # 1. TF-IDF + Cosine Similarity (Layer 1)
        tfidf_score = self._compute_tfidf_similarity(user_answer_clean, ideal_answer)

        # 2. Keyword Coverage (Layer 2)
        keyword_score, keywords_found = self._compute_keyword_score(user_answer_clean, keywords)

        # 3. Gemini Semantic Evaluation (Layer 3)
        gemini_data = self._compute_gemini_semantic_score(question_text, user_answer_clean, ideal_answer)
        
        if gemini_data:
            gemini_score = gemini_data.overall
            strengths = gemini_data.strengths
            weaknesses = gemini_data.weaknesses
            improvement_tip = gemini_data.improvement_tip
        else:
            # Fallback to Layers 1 & 2 only if Gemini fails
            logger.warning("Gemini evaluation failed or skipped. Falling back to TF-IDF & Keywords.")
            gemini_score = (tfidf_score + keyword_score) / 2.0
            strengths = ["Gave an answer containing matching terms."] if tfidf_score > 3.0 else []
            weaknesses = ["Semantic evaluation could not be processed, falling back to keyword similarity."]
            improvement_tip = "Expand your explanation using more precise industry standard keywords."

        # Compute Final Weighted Score (0-10 Scale)
        final_score = round(
            (tfidf_score * self.WEIGHT_TFIDF) +
            (keyword_score * self.WEIGHT_KEYWORD) +
            (gemini_score * self.WEIGHT_GEMINI),
            2
        )

        # Verdict assignment based on final score
        if final_score >= 8.5:
            verdict = "Excellent"
        elif final_score >= 7.0:
            verdict = "Good"
        elif final_score >= 5.0:
            verdict = "Average"
        elif final_score >= 3.0:
            verdict = "Needs Improvement"
        else:
            verdict = "Poor"

        # Heuristic Communication Metrics
        metrics = self._analyze_communication(user_answer_clean, keywords)

        return {
            "score": final_score,
            "tfidf_score": round(tfidf_score, 2),
            "keyword_score": round(keyword_score, 2),
            "gemini_score": round(gemini_score, 2),
            "verdict": verdict,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_tip": improvement_tip,
            "keywords_found": keywords_found,
            "metrics": metrics
        }

    def _compute_tfidf_similarity(self, user_answer: str, ideal_answer: str) -> float:
        """Compute TF-IDF cosine similarity on a 0-10 scale."""
        if not user_answer or not ideal_answer:
            return 0.0
            
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([user_answer.lower(), ideal_answer.lower()])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Convert similarity (0-1) to 0-10 score
            return min(10.0, sim * 10.0)
        except Exception as e:
            logger.error(f"Error computing TF-IDF in evaluation: {e}")
            return 0.0

    def _compute_keyword_score(self, user_answer: str, expected_keywords: list[str]) -> tuple[float, list[str]]:
        """Checks how many expected keywords appear in the answer, returns (score out of 10, found_list)."""
        if not expected_keywords:
            return 10.0, []

        user_lower = user_answer.lower()
        found = []
        
        for kw in expected_keywords:
            # Check for substring match (e.g. 'mutable' matches 'mutability')
            kw_clean = kw.lower().strip()
            # Simple regex search for boundaries or substrings
            if kw_clean in user_lower:
                found.append(kw)

        coverage = len(found) / len(expected_keywords)
        score = coverage * 10.0
        return min(10.0, score), found

    def _compute_gemini_semantic_score(self, question: str, user_answer: str, ideal_answer: str) -> GeminiEvaluationSchema | None:
        """Calls Gemini API for structured evaluation."""
        if not self.gemini_service:
            return None

        prompt = f"""
        You are an expert technical interviewer and ML hiring manager.
        Evaluate the candidate's answer for the following question against the provided ideal answer.
        
        QUESTION:
        {question}
        
        CANDIDATE'S ANSWER:
        {user_answer}
        
        IDEAL REFERENCE ANSWER:
        {ideal_answer}
        
        Analyze the correctness, completeness, clarity, and technical depth.
        Assign scores out of 10 for each dimension, and an overall weighted score.
        Identify 1-3 specific strengths, 1-3 specific gaps or weaknesses, and a concrete improvement tip.
        """
        
        try:
            res = self.gemini_service._call_gemini_with_retry(prompt, GeminiEvaluationSchema)
            return res
        except Exception as e:
            logger.error(f"Gemini semantic evaluation error: {e}")
            return None

    def _analyze_communication(self, answer: str, keywords: list[str]) -> dict:
        """Basic heuristic analysis of the communication quality of the answer."""
        words = answer.split()
        word_count = len(words)
        
        # Detect filler words
        filler_words = ["um", "uh", "like", "basically", "actually", "literally", "sort of", "kind of"]
        filler_count = 0
        answer_lower = answer.lower()
        for f in filler_words:
            # Find occurrences as distinct words
            filler_count += len(re.findall(r'\b' + f + r'\b', answer_lower))

        # Technical depth: ratio of expected keywords used in answer
        keywords_ratio = 0.0
        if words:
            # Let's count how many total keyword mentions are there
            k_mentions = 0
            for kw in keywords:
                k_mentions += len(re.findall(r'\b' + kw.lower() + r'\w*\b', answer_lower))
            keywords_ratio = min(1.0, k_mentions / word_count) if word_count > 0 else 0.0

        # Quality scoring out of 10
        # 10 is ideal length (100-300 words), low fillers, good technical keywords ratio
        length_score = 10.0
        if word_count < 20:
            length_score = 3.0  # too short
        elif word_count < 50:
            length_score = 6.0
        elif word_count > 400:
            length_score = 8.0  # a bit verbose

        filler_penalty = min(5.0, filler_count * 0.5)
        comm_score = max(1.0, length_score - filler_penalty + (keywords_ratio * 10.0))
        
        return {
            "word_count": word_count,
            "filler_word_count": filler_count,
            "technical_depth_score": round(keywords_ratio * 10.0, 2),
            "communication_quality_score": round(min(10.0, comm_score), 2)
        }
