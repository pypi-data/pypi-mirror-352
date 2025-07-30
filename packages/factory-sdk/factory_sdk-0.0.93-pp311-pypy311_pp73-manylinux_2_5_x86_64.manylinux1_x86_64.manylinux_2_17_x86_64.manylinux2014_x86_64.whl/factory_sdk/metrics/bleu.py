from typing import List, Dict
from collections import Counter
import numpy as np

def BLEU(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate BLEU score for text generation evaluation.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            max_ngram: int = 4  # Maximum n-gram size (default is BLEU-4)
            weights: List[float] = None  # Weights for different n-grams
            
    Returns:
        Dictionary with single BLEU score
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    max_ngram = kwargs.get('max_ngram', 4)
    weights = kwargs.get('weights', None)
    
    if weights is None:
        weights = [1.0/max_ngram] * max_ngram
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    def get_ngrams(text: str, n: int) -> Counter:
        tokens = text.split()
        return Counter(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))
    
    total_bleu = 0.0
    
    for i, pred in enumerate(predictions):
        pred_tokens = pred.split()
        ref_tokens = labels[i].split()
        
        if not pred_tokens or not ref_tokens:
            continue
        
        matches_by_n = {}
        possible_matches_by_n = {}
        
        for n in range(1, max_ngram + 1):
            pred_ngrams = get_ngrams(pred, n)
            ref_ngrams = get_ngrams(labels[i], n)
            
            matches = sum((pred_ngrams & ref_ngrams).values())
            total = sum(pred_ngrams.values())
            
            matches_by_n[n] = matches
            possible_matches_by_n[n] = total
        
        bleu_scores = []
        for n in range(1, max_ngram + 1):
            if possible_matches_by_n[n] == 0:
                bleu_scores.append(0.0)
            else:
                bleu_scores.append(matches_by_n[n] / possible_matches_by_n[n])
        
        score = np.exp(np.sum([w * np.log(s) if s > 0 else float('-inf') 
                              for w, s in zip(weights, bleu_scores)]))
        
        bp = 1.0
        if len(pred_tokens) < len(ref_tokens):
            bp = np.exp(1 - len(ref_tokens)/len(pred_tokens))
        
        score *= bp
        total_bleu += score
    
    return {
        'score': total_bleu / len(predictions)
    }