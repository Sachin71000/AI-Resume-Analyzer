import spacy
import spacy.cli
import re

class TextPreprocessor:
    def __init__(self):
        try:
  
  
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            print("Warning: en_core_web_md not found. Downloading now...")
            spacy.cli.download("en_core_web_md")
            self.nlp = spacy.load("en_core_web_md")

    def preprocess(self, text: str) -> dict:
        """
        Cleans text and extracts basic entities like email/phone.
        Tokenizes and lemmatizes using spaCy.
        """
        # Basic cleanup
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
        """Compute semantic similarity between two texts using spaCy embeddings."""
        if not text1.strip() or not text2.strip():
            return 0.0
        doc1 = self.nlp(text1.lower())
        doc2 = self.nlp(text2.lower())
        sim = doc1.similarity(doc2)
        return round(max(0.0, sim) * 100, 2)
