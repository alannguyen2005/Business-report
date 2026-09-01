# Retrain Protocol Reference

> Protocol for retraining the winning model on full data after evaluation.

## Why Retrain on Full Data?

During evaluation, we used 80% for training and 20% for testing. The test set was "held out" purely for honest evaluation. Now that we've selected the winner, we want to maximize data utilization:

```
Evaluation phase:    [──── Train (80%) ────][── Test (20%) ──]
                                              ↑ used for evaluation only

Finalization phase:  [──────────── Full Data (100%) ─────────────]
                     ↑ retrain winner on everything for production predictions
```

**The winning model's hyperparameters were validated on the test set. Retraining on full data preserves those hyperparameters while giving the model more training data.**

---

## Retrain Protocol

### Step 1: Retrieve Winning Configuration
```python
# From evaluation_result.json
winner_model_type = eval_result["winner"]["model_type"]

# From model_result_{type}.json
winner_params = winner_result["model_params"]
# Use EXACT same parameters — do not re-tune
```

### Step 2: Combine Train + Test
```python
full_X = pd.concat([X_train, X_test]).reset_index(drop=True)
full_y = pd.concat([y_train, y_test]).reset_index(drop=True)

# For forecasting: ensure chronological order
if pipeline_type == "forecasting":
    full_df = full_df.sort_values(date_col).reset_index(drop=True)
```

### Step 3: Retrain with Same Parameters
```python
# Example for XGBoost:
model = xgb.XGBRegressor(**winner_params)
model.fit(full_X, full_y)
# No eval_set (no holdout) — we already validated the configuration

# Example for SARIMA:
model = pm.ARIMA(order=winner_order, seasonal_order=winner_seasonal_order)
model.fit(full_series)
```

### Step 4: Generate Production Predictions
```python
# Forecasting: predict future periods
if pipeline_type == "forecasting":
    forecast_horizon = test_size  # same horizon as evaluation
    predictions = model.predict(n_periods=forecast_horizon)

# Regression: predictions on any new data
elif pipeline_type == "regression":
    predictions = model.predict(new_X)

# Classification: probabilities for threshold application
elif pipeline_type == "classification":
    probabilities = model.predict_proba(full_X)[:, 1]
```

---

## Rules

1. **Use exact same hyperparameters** — Do NOT re-tune. The evaluation validated these parameters.
2. **No early stopping on retrain** — Use the fixed `best_iteration` from evaluation.
3. **For SMOTE models** — Apply SMOTE on full data before retraining (same configuration).
4. **Preserve preprocessing** — Use the same scaler, encoder, feature engineering as before.
5. **Log retrain metrics** — Cannot compute test metrics (no holdout), but log training metrics for sanity check.

---

## Sanity Checks

```python
# Training metrics should be similar to or better than evaluation metrics
retrain_train_metric = compute_metric(full_y, model.predict(full_X))
eval_test_metric = eval_result["winner"]["primary_value"]

# If retrain metric is MUCH better than eval → expected (no holdout)
# If retrain metric is WORSE than eval → something went wrong

if retrain_train_metric > eval_test_metric * 1.5:
    # For lower-is-better metrics, this means retrain is much worse
    warn("Retrained model performs worse than evaluation — investigate")
```

---

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Re-tuning hyperparameters** | Invalidates evaluation results | Use exact same params |
| **Different preprocessing** | Feature mismatch between eval and retrain | Use same scaler/encoder objects |
| **Forgetting SMOTE** | Retrained model sees imbalanced data | Apply same SMOTE config on full data |
| **Early stopping without eval_set** | Can't early-stop without holdout | Use fixed `best_iteration` from eval |
| **Not sorting time series** | Chronological order broken | Sort by date before retraining forecasting models |
