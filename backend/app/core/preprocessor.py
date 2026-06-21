import re
import logging

logger = logging.getLogger(__name__)

# NLTK replaces spaCy — uses ~20MB vs spaCy's ~150MB on Render free tier
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def _ensure_nltk_data():
    """Download required NLTK data if not already present."""
    for resource, path in [
        ('wordnet',   'corpora/wordnet'),
        ('stopwords', 'corpora/stopwords'),
        ('punkt',     'tokenizers/punkt'),
        ('omw-1.4',   'corpora/omw-1.4'),
    ]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

_ensure_nltk_data()

class TextPreprocessor:
    def __init__(self):
        self._lemmatizer = WordNetLemmatizer()
        self._stop_words = set(stopwords.words('english'))

    def preprocess(self, text: str) -> dict:
        """
        Cleans text and extracts basic entities like email/phone.
        Tokenizes and lemmatizes using NLTK (replaces spaCy to save ~130MB RAM).
        """
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        # Extract phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\\s]?\d{3}[-.\\s]?\d{4}', text)

        # Remove extra whitespace and special characters, but preserve / & - for skill names
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,;+)(#%/&\-]', ' ', text)
        clean_text = ' '.join(clean_text.split())

        # Tokenize + lemmatize (lowercase, remove stopwords + punctuation)
        tokens = []
        for word in re.findall(r'[a-zA-Z]+', clean_text.lower()):
            if word not in self._stop_words and len(word) > 1:
                tokens.append(self._lemmatizer.lemmatize(word))

        processed_text = " ".join(tokens)

        return {
            'raw_clean': clean_text,
            'processed': processed_text,
            'emails': list(set(emails)),
            'phones': list(set(phones))
        }

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts (pure Python, no sklearn)."""
        from .similarity import cosine_similarity_texts
        return cosine_similarity_texts(text1, text2)

