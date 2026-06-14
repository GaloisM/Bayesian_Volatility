# Bayesian Volatility

Notebook-first research project for forecasting realized volatility with
classical HAR and Bayesian HAR models.

The main artifact is:

- `bayesian_volatility_clean.ipynb` - organized research notebook matching the
  presentation narrative

The original exploratory notebook is kept as:

- `prep_data.ipynb`

## Research Question

Can a Bayesian HAR model improve 5-day realized-volatility forecasts and
high-volatility warnings compared with simple classical HAR baselines?

The target is:

```text
RV_t = log(S_t / S_{t-1})^2
RV_forward_5 = mean(RV_{t+1}, ..., RV_{t+5})
```

The main regression scale is `log(RV_forward_5)`.

## Notebook Structure

The clean notebook follows the presentation:

1. Data and target definition
2. HAR feature construction
3. Classical OLS/Ridge HAR baselines
4. Jump/regime HAR extension
5. Log-HAR model diagnostics
6. Naive benchmark comparison
7. Bayesian HAR with Normal likelihood
8. Bayesian HAR with Student-t likelihood
9. Posterior predictive intervals
10. High-volatility warning signals

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then open:

```text
bayesian_volatility_clean.ipynb
```

## Statistical Notes

Use OLS and Ridge as interpretable benchmarks. Treat the Bayesian Student-t HAR
model as the main specification, because volatility residuals are spike-prone
and heavy-tailed.

Report more than point error:

- RMSE, MAE, R2 on `log(RV)`
- RMSE, MAE, R2 on the variance scale
- QLIKE
- 80% and 95% posterior predictive interval coverage
- precision, recall, and F1 for high-volatility warning flags

## Repo Hygiene

Do not commit virtual environments, raw cached data, generated outputs, or large
notebook scratch outputs.
