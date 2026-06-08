from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MatchResult:
    overall_score: float
    tfidf_score: float
    semantic_score: float
    skill_match_score: float
    section_coverage_score: float
    keyword_density_score: float
    top_keywords: List[str] = field(default_factory=list)

class MatchingEngine:
    # Hybrid weights
    WEIGHT_TFIDF = 0.25
    WEIGHT_SEMANTIC = 0.20
    WEIGHT_SKILL = 0.30
    WEIGHT_SECTION = 0.15
    WEIGHT_KEYWORD = 0.10

    @staticmethod
    def _compute_tfidf(resume_text: str, jd_text: str) -> tuple:
        """Compute TF-IDF cosine similarity and extract top keywords."""
        if not resume_text.strip() or not jd_text.strip():
            return 0.0, []

        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            return 0.0, []

        # Top keywords from JD
        try:
            jd_vector = vectorizer.transform([jd_text]).toarray()[0]
            feature_names = vectorizer.get_feature_names_out()
            top_indices = jd_vector.argsort()[::-1][:15]
            top_keywords = [feature_names[i] for i in top_indices if jd_vector[i] > 0]
        except Exception:
            top_keywords = []

        return round(sim * 100, 2), top_keywords

    @staticmethod
    def _compute_keyword_density(resume_text: str, top_keywords: List[str]) -> float:
        """Check what fraction of top JD keywords appear in the resume."""
        if not top_keywords:
            return 0.0
        resume_lower = resume_text.lower()
        found = sum(1 for kw in top_keywords if kw.lower() in resume_lower)
        return round(found / len(top_keywords) * 100, 2)

    @staticmethod
    def compute_match(
        resume_text: str,
        jd_text: str,
        skill_match_pct: float = 0.0,
        section_coverage_pct: float = 0.0,
        semantic_score: float = 0.0
    ) -> MatchResult:
        """
        Compute hybrid match score:
        - TF-IDF cosine similarity (25%)
        - Semantic similarity (20%)
        - Skill overlap (30%)
        - Section coverage (15%)
        - Keyword density (10%)
        """
        tfidf_score, top_keywords = MatchingEngine._compute_tfidf(resume_text, jd_text)
        keyword_density = MatchingEngine._compute_keyword_density(resume_text, top_keywords)

        overall = round(
            tfidf_score * MatchingEngine.WEIGHT_TFIDF +
            semantic_score * MatchingEngine.WEIGHT_SEMANTIC +
            skill_match_pct * MatchingEngine.WEIGHT_SKILL +
            section_coverage_pct * MatchingEngine.WEIGHT_SECTION +
            keyword_density * MatchingEngine.WEIGHT_KEYWORD,
            2
        )

        return MatchResult(
            overall_score=overall,
            tfidf_score=tfidf_score,
            semantic_score=semantic_score,
            skill_match_score=skill_match_pct,
            section_coverage_score=section_coverage_pct,
            keyword_density_score=keyword_density,
            top_keywords=top_keywords
        )
