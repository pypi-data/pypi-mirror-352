from typing import List, Dict

def WordErrorRate(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate Word Error Rate (WER) between predictions and labels.
    WER = (Substitutions + Deletions + Insertions) / Number of Reference Words
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            
    Returns:
        Dictionary with WER score
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    def levenshtein_distance(pred_tokens: List[str], ref_tokens: List[str]) -> int:
        # Create matrix of size (m+1)x(n+1)
        m, n = len(pred_tokens), len(ref_tokens)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if pred_tokens[i-1] == ref_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,    # deletion
                        dp[i][j-1] + 1,    # insertion
                        dp[i-1][j-1] + 1   # substitution
                    )
        
        return dp[m][n]
    
    total_wer = 0.0
    for pred, ref in zip(predictions, labels):
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        
        if not ref_tokens:
            if pred_tokens:
                total_wer += 1
            continue
            
        distance = levenshtein_distance(pred_tokens, ref_tokens)
        wer = distance / len(ref_tokens)
        total_wer += wer
    
    return {
        'score': total_wer / len(predictions)
    }