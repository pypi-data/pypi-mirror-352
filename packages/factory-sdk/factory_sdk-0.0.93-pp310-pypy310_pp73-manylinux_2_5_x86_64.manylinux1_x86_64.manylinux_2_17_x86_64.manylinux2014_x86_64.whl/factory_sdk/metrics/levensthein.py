from typing import List, Dict

def LevenshteinDistance(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate average normalized Levenshtein distance (edit distance).
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            normalize: bool = True  # Whether to normalize by reference length
            
    Returns:
        Dictionary with Levenshtein distance score
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    normalize = kwargs.get('normalize', True)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    def edit_distance(pred: str, ref: str) -> int:
        m, n = len(pred), len(ref)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if pred[i-1] == ref[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,    # deletion
                        dp[i][j-1] + 1,    # insertion
                        dp[i-1][j-1] + 1   # substitution
                    )
        
        return dp[m][n]
    
    total_distance = 0.0
    for pred, ref in zip(predictions, labels):
        distance = edit_distance(pred, ref)
        if normalize:
            # Normalize by length of reference string
            distance = distance / max(len(ref), 1)
        total_distance += distance
    
    return {
        'score': total_distance / len(predictions)
    }