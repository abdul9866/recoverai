"""
Evaluation Metrics Engine for RecoverAI.
Computes Detection Accuracy, False Retirement Rate (FRR), Precision@K, and Time to Detect.
"""
from typing import List, Dict, Set, Any

def detection_accuracy(predicted_labels: List[Any], true_labels: List[Any]) -> float:
    """Computes categorical classification accuracy for recoverability predictor."""
    if not true_labels:
        return 0.0
    correct = sum(1 for p, t in zip(predicted_labels, true_labels) if p == t)
    return float(correct / len(true_labels))

def false_retirement_rate(
    predicted_unrecoverable_ids: List[str],
    actually_recovered_ids: List[str]
) -> float:
    """
    Computes False Retirement Rate (FRR):
    The fraction of files incorrectly retired as 'unrecoverable' (effort=SKIP)
    that full carving would have successfully recovered.
    """
    if not predicted_unrecoverable_ids:
        return 0.0
    unrec_set = set(predicted_unrecoverable_ids)
    rec_set = set(actually_recovered_ids)
    false_positives = len(unrec_set & rec_set)
    return float(false_positives / len(predicted_unrecoverable_ids))

def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int = 5) -> float:
    """Computes Precision@K for search retrieval performance."""
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant_ids)
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return float(hits / min(k, len(top_k)))

def time_to_detect(result_log: List[Dict[str, Any]]) -> float:
    """Computes average time (seconds) taken to recover target files."""
    successful_times = [
        r["time_taken_s"] for r in result_log if r.get("success", False) or r.get("bytes_recovered", 0) > 0
    ]
    if not successful_times:
        return float("nan")
    return float(sum(successful_times) / len(successful_times))
