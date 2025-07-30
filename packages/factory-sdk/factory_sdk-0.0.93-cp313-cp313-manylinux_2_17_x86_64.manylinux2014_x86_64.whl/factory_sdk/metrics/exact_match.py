from typing import List, Dict
import string

def ExactMatch(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate the exact match score between predictions and labels.
    Exact match requires perfect character-for-character matching.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            normalize_whitespace: bool = True  # Whether to normalize whitespace
            strip_punctuation: bool = False  # Whether to remove punctuation
            
    Returns:
        Dictionary with exact match score
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    normalize_whitespace = kwargs.get('normalize_whitespace', True)
    strip_punctuation = kwargs.get('strip_punctuation', False)
    
    def normalize(text: str) -> str:
        if not case_sensitive:
            text = text.lower()
        if normalize_whitespace:
            text = ' '.join(text.split())
        if strip_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        return text
    
    predictions = [normalize(p) for p in predictions]
    labels = [normalize(l) for l in labels]
    
    matches = sum(1 for p, l in zip(predictions, labels) if p == l)
    exact_match_score = matches / len(predictions) if predictions else 0.0
    
    return {
        'score': exact_match_score
    }

