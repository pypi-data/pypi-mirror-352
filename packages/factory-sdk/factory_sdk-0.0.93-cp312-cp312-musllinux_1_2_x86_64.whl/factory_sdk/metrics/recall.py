from typing import List, Dict
import numpy as np

def Recall(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate recall for a specific target class.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            target_class: str  # The target class to calculate recall for
            
    Returns:
        Dictionary with recall score for target class
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    target_class = kwargs.get('target_class')
    
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
    actual_positives = sum(1 for l in labels if l == target_class)
    
    recall = true_positives / actual_positives if actual_positives > 0 else 0.0
    
    return {
        'score': recall
    }

def RecallOneVsRest(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate one-vs-rest recall for all classes.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            
    Returns:
        Dictionary with recall scores per class and macro avg
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    unique_classes = sorted(set(labels))
    recalls = {}
    
    for cls in unique_classes:
        # For current class vs rest
        true_positives = sum(1 for p, l in zip(predictions, labels) 
                           if p == cls and l == cls)
        total_actual = sum(1 for l in labels if l == cls)
        
        recall = true_positives / total_actual if total_actual > 0 else 0.0
        recalls[f'recall_{cls}'] = recall
    
    # Add macro average
    macro_avg_recall = np.mean(list(recalls.values()))
    
    return {
        "score": macro_avg_recall,
    }