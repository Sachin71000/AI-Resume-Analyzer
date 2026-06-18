import spacy
import spacy.cli
import re
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    def __init__(self):
        # Use en_core_web_sm (30MB RAM) instead of en_core_web_md (200MB RAM)
        # to stay within Render free tier 512MB limit
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("en_core_web_sm not found. Downloading now...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def preprocess(self, text: str) -> dict:
        """
        Cleans text and extracts basic entities like email/phone.
        Tokenizes and lemmatizes using spaCy.
        """
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        # Optional: Extract phone numbers (simple regex)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)

        # Remove extra whitespace and special characters, but preserve / & - for skill names
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,;+)(#%/&\-]', ' ', text)
        clean_text = ' '.join(clean_text.split())

        # spaCy processing (lowercase the text to unify)
        doc = self.nlp(clean_text.lower())
        
        tokens = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                tokens.append(token.lemma_)

        processed_text = " ".join(tokens)

        return {
            'raw_clean': clean_text,
            'processed': processed_text,
            'emails': list(set(emails)),
            'phones': list(set(phones))
        }

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity between two texts using TF-IDF cosine similarity.
        
        Uses scikit-learn TF-IDF instead of spaCy word vectors so we can use
        the lightweight en_core_web_sm model (no vectors) and save ~170MB RAM.
        """
        if not text1.strip() or not text2.strip():
            return 0.0
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform([text1.lower(), text2.lower()])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(round(max(0.0, sim) * 100, 2))
        except Exception:
            return 0.0

