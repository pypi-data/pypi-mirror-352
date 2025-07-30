from typing import List, Dict

def ROUGE_L(
    predictions: List[str],
    labels: List[str],
    **kwargs
) -> Dict[str, float]:
    """
    Calculate ROUGE-L score using longest common subsequence.
    
    Args:
        predictions: List of predicted strings
        labels: List of reference/ground truth strings
        **kwargs:
            case_sensitive: bool = False  # Whether comparison should be case-sensitive
            beta: float = 1.2  # Beta parameter for f-measure calculation
            
    Returns:
        Dictionary with single ROUGE-L score
    """
    if len(predictions) != len(labels):
        raise ValueError("Predictions and labels must have the same length")
    
    case_sensitive = kwargs.get('case_sensitive', False)
    beta = kwargs.get('beta', 1.2)
    
    if not case_sensitive:
        predictions = [p.lower().strip() for p in predictions]
        labels = [l.lower().strip() for l in labels]
    
    def lcs_length(pred_tokens: List[str], ref_tokens: List[str]) -> int:
        m, n = len(pred_tokens), len(ref_tokens)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if pred_tokens[i-1] == ref_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    total_score = 0.0
    for pred, ref in zip(predictions, labels):
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        
        if not pred_tokens or not ref_tokens:
            continue
        
        lcs = lcs_length(pred_tokens, ref_tokens)
        
        # Compute precision and recall
        precision = lcs / len(pred_tokens) if pred_tokens else 0
        recall = lcs / len(ref_tokens) if ref_tokens else 0
        
        # Compute F-measure
        if precision + recall > 0:
            score = ((1 + beta**2) * precision * recall) / (beta**2 * precision + recall)
        else:
            score = 0.0
            
        total_score += score
    
    return {
        'score': total_score / len(predictions)
    }