from typing import List, Dict
import numpy as np

def F1Score(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate F1 score for a specific target class.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            target_class: str  # The target class to calculate F1 for
            epsilon: float = 1e-7  # Small constant to avoid division by zero
            
    Returns:
        Dictionary with F1 score for target class
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    target_class = kwargs.get('target_class')
    epsilon = kwargs.get('epsilon', 1e-7)
    
    if target_class is None:
        raise ValueError("target_class must be specified in kwargs")
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
        target_class = target_class.lower().strip()
    else:
        predictions = [p.strip() for p in predictions]
        labels = [l.strip() for l in labels]
        target_class = target_class.strip()
    
    true_positives = sum(1 for p, l in zip(predictions, labels) 
                        if p == l and l == target_class)
    predicted_positives = sum(1 for p in predictions if p == target_class)
    actual_positives = sum(1 for l in labels if l == target_class)
    
    precision = true_positives / (predicted_positives + epsilon) if predicted_positives > 0 else 0.0
    recall = true_positives / (actual_positives + epsilon) if actual_positives > 0 else 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall + epsilon) if (precision + recall) > 0 else 0.0
    
    return {
        'score': f1
    }


def F1OneVsRest(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate one-vs-rest F1 scores for all classes.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            epsilon: float = 1e-7  # Small constant to avoid division by zero
            
    Returns:
        Dictionary with F1 scores per class and macro avg
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    epsilon = kwargs.get('epsilon', 1e-7)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    unique_classes = sorted(set(labels))
    f1_scores = {}
    
    for cls in unique_classes:
        # Calculate true positives, predicted positives, and actual positives
        true_positives = sum(1 for p, l in zip(predictions, labels) 
                           if p == cls and l == cls)
        predicted_positives = sum(1 for p in predictions if p == cls)
        actual_positives = sum(1 for l in labels if l == cls)
        
        # Calculate precision and recall
        precision = true_positives / (predicted_positives + epsilon) if predicted_positives > 0 else 0.0
        recall = true_positives / (actual_positives + epsilon) if actual_positives > 0 else 0.0
        
        # Calculate F1
        f1 = 2 * (precision * recall) / (precision + recall + epsilon) if (precision + recall) > 0 else 0.0
        f1_scores[f'f1_{cls}'] = f1
    
    macro_avg_f1 = np.mean(list(f1_scores.values()))
    
    return {
        'score': macro_avg_f1,
    }