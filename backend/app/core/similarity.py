"""
Pure Python cosine similarity — replaces scikit-learn + scipy (~120MB saved).

Uses bag-of-words TF-weighted cosine similarity. Quality is nearly identical
to sklearn's TF-IDF for short texts (resumes, JDs, interview answers).
No external dependencies required.
"""
import re
import math
from collections import Counter
from typing import List, Tuple

# Common English stopwords (inline — avoids NLTK corpus load for this module)
_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'not', 'no', 'nor', 'so',
    'yet', 'both', 'either', 'neither', 'as', 'if', 'then', 'than', 'that',
    'this', 'these', 'those', 'it', 'its', 'we', 'our', 'you', 'your',
    'he', 'she', 'they', 'their', 'my', 'me', 'him', 'her', 'us', 'them',
    'i', 'am', 'into', 'up', 'out', 'about', 'also', 'just', 'more',
    'other', 'such', 'same', 'all', 'each', 'any', 'one', 'two',
}


def _tokenize(text: str) -> List[str]:
    """Lowercase, extract alphabetic tokens, remove stopwords."""
    return [w for w in re.findall(r'[a-zA-Z]+', text.lower())
            if w not in _STOPWORDS and len(w) > 1]


def _term_freq(tokens: List[str]) -> Counter:
    """Raw term frequency vector."""
    return Counter(tokens)


def cosine_similarity_texts(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts on a 0–100 scale.
    Uses bag-of-words (term frequency) vectors — no external libraries.
    Returns 0.0 if either text is empty.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    vec1 = _term_freq(_tokenize(text1))
    vec2 = _term_freq(_tokenize(text2))

    # Dot product over common terms
    common = set(vec1) & set(vec2)
    dot = sum(vec1[w] * vec2[w] for w in common)

    if dot == 0:
        return 0.0

    mag1 = math.sqrt(sum(v * v for v in vec1.values()))
    mag2 = math.sqrt(sum(v * v for v in vec2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    sim = dot / (mag1 * mag2)
    return float(round(min(1.0, sim) * 100, 2))


def cosine_similarity_score_10(text1: str, text2: str) -> float:
    """
    Same as cosine_similarity_texts but returns a 0–10 scale score.
    Used by the interview evaluator.
    """
    return round(cosine_similarity_texts(text1, text2) / 10.0, 2)
