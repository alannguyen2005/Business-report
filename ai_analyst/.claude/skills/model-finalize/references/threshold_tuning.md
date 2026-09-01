# Threshold Tuning Reference

> For classification models — optimizing the probability threshold for business objectives.

## Why Threshold Tuning?

Default threshold = 0.5 assumes:
- Equal cost of false positives and false negatives
- Balanced classes
- Maximum accuracy is the goal

**All three assumptions are usually WRONG for business problems.**

```
Example: Churn prediction
  FP cost = $50 (unnecessary outreach to non-churner)
  FN cost = $5,000 (lost customer lifetime value)
  → FN is 100x more costly than FP
  → Optimal threshold << 0.5
```

---

## Method 1: F1-Maximizing Threshold

Find the threshold that maximizes F1-Score on validation data.

```python
import numpy as np
from sklearn.metrics import f1_score

def find_f1_optimal_threshold(y_true, y_prob, n_thresholds=100):
    """
    Find threshold that maximizes F1-Score.
    
    Parameters:
        y_true: array of true binary labels
        y_prob: array of predicted probabilities
        n_thresholds: number of thresholds to evaluate
    
    Returns:
        optimal_threshold, max_f1, all_results
    """
    thresholds = np.linspace(0.05, 0.95, n_thresholds)
    results = []
    
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        results.append({'threshold': t, 'f1': f1})
    
    best = max(results, key=lambda x: x['f1'])
    return best['threshold'], best['f1'], results
```

**When to use:** Default choice when no cost information is available.

---

## Method 2: Cost-Based Threshold

Minimize total business cost based on misclassification costs.

```python
def find_cost_optimal_threshold(y_true, y_prob, cost_FP, cost_FN, n_thresholds=100):
    """
    Find threshold that minimizes total misclassification cost.
    
    Parameters:
        cost_FP: cost of false positive (e.g., $50 for unnecessary outreach)
        cost_FN: cost of false negative (e.g., $5000 for missed churn)
    
    Returns:
        optimal_threshold, min_cost, all_results
    """
    thresholds = np.linspace(0.05, 0.95, n_thresholds)
    results = []
    
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        fp = ((y_pred == 1) & (y_true == 0)).sum()
        fn = ((y_pred == 0) & (y_true == 1)).sum()
        total_cost = fp * cost_FP + fn * cost_FN
        results.append({'threshold': t, 'cost': total_cost, 'fp': fp, 'fn': fn})
    
    best = min(results, key=lambda x: x['cost'])
    return best['threshold'], best['cost'], results
```

**When to use:** When business can estimate cost of FP and FN.

### Common Cost Ratios

| Domain | FP Cost | FN Cost | Typical Optimal Threshold |
|--------|---------|---------|---------------------------|
| Churn prevention | $50 (outreach) | $5,000 (lost LTV) | 0.05 - 0.15 |
| Fraud detection | $10 (manual review) | $10,000 (fraud loss) | 0.01 - 0.10 |
| Lead scoring | $100 (sales time) | $5,000 (missed deal) | 0.10 - 0.20 |
| Medical screening | $200 (follow-up test) | $50,000 (missed diagnosis) | 0.02 - 0.10 |
| Spam filtering | $5 (missed email) | $0.01 (read spam) | 0.80 - 0.95 |

---

## Method 3: Precision-Recall Curve Analysis

```python
from sklearn.metrics import precision_recall_curve

def precision_recall_analysis(y_true, y_prob):
    """
    Analyze precision-recall trade-off across thresholds.
    """
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
    
    # Find threshold where precision = recall (balanced point)
    diffs = np.abs(precisions[:-1] - recalls[:-1])
    balanced_idx = np.argmin(diffs)
    balanced_threshold = thresholds[balanced_idx]
    
    # Find threshold for minimum recall target
    def threshold_for_min_recall(target_recall):
        valid = recalls[:-1] >= target_recall
        if valid.any():
            idx = np.where(valid)[0][-1]  # highest threshold meeting target
            return thresholds[idx]
        return 0.01  # fallback to very low threshold
    
    return {
        'balanced_threshold': balanced_threshold,
        'threshold_recall_80': threshold_for_min_recall(0.80),
        'threshold_recall_90': threshold_for_min_recall(0.90),
        'threshold_recall_95': threshold_for_min_recall(0.95)
    }
```

---

## Threshold Validation

After selecting a threshold, validate it with cross-validation:

```python
from sklearn.model_selection import StratifiedKFold

def validate_threshold(model, X, y, threshold, n_splits=5):
    """
    Validate that the selected threshold is stable across folds.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_metrics = []
    
    for train_idx, val_idx in skf.split(X, y):
        model_cv = clone(model)
        model_cv.fit(X.iloc[train_idx], y.iloc[train_idx])
        probs = model_cv.predict_proba(X.iloc[val_idx])[:, 1]
        preds = (probs >= threshold).astype(int)
        
        fold_metrics.append({
            'f1': f1_score(y.iloc[val_idx], preds),
            'precision': precision_score(y.iloc[val_idx], preds),
            'recall': recall_score(y.iloc[val_idx], preds)
        })
    
    # Check stability
    f1_values = [m['f1'] for m in fold_metrics]
    cv_std = np.std(f1_values)
    
    return {
        'mean_f1': np.mean(f1_values),
        'std_f1': cv_std,
        'stable': cv_std < 0.05,  # Threshold is stable if CV std < 5%
        'fold_metrics': fold_metrics
    }
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Using default 0.5** | Suboptimal for imbalanced data | Always tune threshold |
| **Tuning on test set** | Overfitting threshold to test data | Use CV on training data for threshold selection |
| **Ignoring cost asymmetry** | Treating FP and FN equally | Ask business for cost estimates |
| **Unstable threshold** | Threshold changes across folds | Use wider search grid; consider ensemble of thresholds |
| **Extreme threshold** | threshold < 0.05 or > 0.95 | Acceptable if cost ratio justifies it, but flag for review |
