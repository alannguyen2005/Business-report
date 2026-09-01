# Decision Tree Classification Guide

> Single tree classifier — maximum interpretability with visual rule extraction.

## Algorithm Overview

A Decision Tree recursively splits data based on feature thresholds to create a tree of rules:

```
                    [days_since_login > 45?]
                    /                      \
                  Yes                       No
           [support_tickets > 3?]     [monthly_spend > $50?]
           /                 \         /                  \
         Yes                 No      Yes                  No
      CHURN (85%)      CHURN (45%)  STAY (92%)      CHURN (35%)
```

Each leaf node gives a prediction based on the majority class of training samples that reached it.

---

## Implementation

```python
from sklearn.tree import DecisionTreeClassifier, export_text

def train_decision_tree(X_train, y_train, X_test):
    """
    Train Decision Tree classifier with controlled depth.
    """
    model = DecisionTreeClassifier(
        max_depth=5,              # Prevent overfitting
        class_weight='balanced',  # Handle imbalance
        min_samples_split=10,     # Min samples to create a split
        min_samples_leaf=5,       # Min samples in leaf
        criterion='gini',         # or 'entropy'
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    
    # Extract human-readable rules
    tree_rules = export_text(model, feature_names=list(X_train.columns), max_depth=5)
    
    # Feature importance
    importance = dict(zip(X_train.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'model': model,
        'predictions': predictions,
        'probabilities': probabilities,
        'feature_importance': importance,
        'tree_rules': tree_rules,
        'n_leaves': model.get_n_leaves(),
        'tree_depth': model.get_depth()
    }
```

---

## Hyperparameters

| Parameter | Default | Range | Description | Tuning Guide |
|---|---|---|---|---|
| `max_depth` | 5 | 3-10 | Max tree depth | 5 = good balance of accuracy and interpretability. >7 = hard to visualize |
| `min_samples_split` | 10 | 2-50 | Min samples to split | Higher = fewer, more reliable splits |
| `min_samples_leaf` | 5 | 1-20 | Min samples in leaf | Higher = smoother predictions, fewer edge cases |
| `class_weight` | 'balanced' | 'balanced' or dict | Class weight adjustment | Always 'balanced' for imbalanced data |
| `criterion` | 'gini' | 'gini', 'entropy' | Split quality measure | 'gini' is faster; 'entropy' sometimes better |
| `max_features` | None | 'sqrt', 'log2', None | Features to consider per split | None = all features. 'sqrt' adds randomness |

### Depth vs Interpretability Trade-off
```
max_depth=3:  8 leaf nodes,   easy to explain to stakeholders
max_depth=5:  32 leaf nodes,  good balance
max_depth=7:  128 leaf nodes, hard to visualize, better accuracy
max_depth=10: 1024 leaf nodes, essentially a black box
```

---

## Best Practices

1. **Limit depth to 5** — Deep trees overfit and lose interpretability.
2. **Always use `class_weight='balanced'`** — Prevents tree from ignoring minority class.
3. **Extract and present rules** — Decision trees' biggest advantage is explainability.
4. **Use as diagnostic tool** — Even if RF/XGBoost wins, tree rules explain which features matter.
5. **Prune aggressively** — `min_samples_leaf=5` prevents overfitting on small groups.

### Extracting Business Rules
```python
from sklearn.tree import export_text

rules = export_text(model, feature_names=list(X_train.columns))
print(rules)

# Output example:
# |--- days_since_login > 45.00
# |   |--- support_tickets > 3.00
# |   |   |--- class: 1 (churn)
# |   |--- support_tickets <= 3.00
# |   |   |--- monthly_spend <= 25.00
# |   |   |   |--- class: 1 (churn)
# |   |   |--- monthly_spend > 25.00
# |   |   |   |--- class: 0 (stay)
# |--- days_since_login <= 45.00
# |   |--- class: 0 (stay)

# Business interpretation:
# "Customers who haven't logged in for 45+ days AND have 3+ support tickets
#  are at highest risk of churn"
```

### Visualizing the Tree
```python
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(20, 10))
plot_tree(model, feature_names=list(X_train.columns),
          class_names=['Stay', 'Churn'], filled=True,
          rounded=True, ax=ax, fontsize=10, max_depth=3)
plt.tight_layout()
plt.savefig('decision_tree.png', dpi=150)
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Too deep** | Overfitting (train F1=1.0, test F1=0.3) | Set `max_depth=5` |
| **No depth limit** | Tree memorizes training data | Always constrain depth |
| **Ignoring rules** | Using tree only for prediction | Extract and present rules to stakeholders |
| **Unstable splits** | Small data changes → different tree | Expected limitation. Use RF for stability |
| **Biased splits** | Favors high-cardinality features | Pre-encode categoricals; use max_features='sqrt' |

---

## When Decision Tree Works Best

- **Interpretability is top priority** — Stakeholders need to understand the rules
- **Rule extraction** — "Give me the top 3 rules for identifying at-risk customers"
- **Small to medium data** (100-10K rows) — Enough to learn patterns
- **Diagnostic complement** — Use alongside RF/XGBoost to explain what's driving predictions

## When Decision Tree Struggles

- **Large, complex datasets** — Single tree underfits; use ensemble (RF/XGBoost)
- **Continuous relationships** — Trees approximate with step functions
- **Unstable splits** — Different random seed → different tree (use RF for stability)
