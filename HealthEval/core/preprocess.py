import re

class Preprocessor:
    """
    Preprocesses health queries for model input.
    Community note: Basic cleaning; extend for advanced NLP preprocessing if needed.
    """
    def process_query(self, query: str) -> str:
        """
        Clean and format the query.
        Community note: Removes extra whitespace and normalizes punctuation.
        """
        if not query:
            return ""
        # Basic cleaning
        query = re.sub(r'\s+', ' ', query.strip())
        query = re.sub(r'[^\w\s\?\.\,\!\-\']', '', query)  # Keep common punctuation
        return query