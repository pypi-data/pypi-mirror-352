from typing import List, Dict
import numpy as np

def Precision(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate precision for a specific target class.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            target_class: str  # The target class to calculate precision for
            
    Returns:
        Dictionary with precision score for target class
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
    predicted_positives = sum(1 for p in predictions if p == target_class)
    
    precision = true_positives / predicted_positives if predicted_positives > 0 else 0.0
    
    return {
        'score': precision
    }

def PrecisionOneVsRest(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate one-vs-rest precision for all classes.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            
    Returns:
        Dictionary with precision scores per class and macro avg
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    unique_classes = sorted(set(labels))
    precisions = {}
    
    for cls in unique_classes:
        # For current class vs rest
        true_positives = sum(1 for p, l in zip(predictions, labels) 
                           if p == cls and l == cls)
        total_predicted = sum(1 for p in predictions if p == cls)
        
        precision = true_positives / total_predicted if total_predicted > 0 else 0.0
        precisions[f'precision_{cls}'] = precision
    
    # Add macro average
    macro_avg_precision = np.mean(list(precisions.values()))
    
    return {
        "score": macro_avg_precision,
    }