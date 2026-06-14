# Bayesian Volatility

Minimal research repo for forecasting realized volatility with Bayesian HAR
models.

The aim is statistical development, not application infrastructure. Keep the
repo small:

- `prep_data.ipynb` - exploratory analysis and figures
- `volatility_models.py` - reusable statistical functions
- `requirements.txt` - Python dependencies

## Statistical Direction

The core object is 5-day forward realized variance:

```text
RV_t = log(P_t / P_{t-1})^2
RV_forward_5 = mean(RV_{t+1}, ..., RV_{t+5})
```

The first serious model family should be HAR on log realized variance:

```text
log(RV_forward_5) ~ log(RV_lag_1) + log(RV_mean_5) + log(RV_mean_22)
```

Use OLS/Ridge only as benchmarks. The main model should be Bayesian HAR with a
Student-t likelihood, because volatility forecast errors are heavy-tailed and
spike-prone.

## Evaluation

Use metrics that make sense for volatility:

- RMSE/MAE/R2 on `log(RV)`
- RMSE/MAE/R2 on the variance scale
- QLIKE loss
- posterior predictive interval coverage
- warning-signal precision/recall/F1 for high-volatility regimes

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Example Use

Inside the notebook:

```python
import yfinance as yf
from volatility_models import (
    TARGET,
    make_har_dataset,
    train_test_split_time,
    fit_har_benchmarks,
    fit_bayesian_har,
    evaluate_log_forecast,
    evaluate_posterior_predictive,
)

prices = yf.download("^GSPC", start="2010-01-01", end="2023-01-01", auto_adjust=True)
close = prices["Close"]

data = make_har_dataset(close)
train, test = train_test_split_time(data)

benchmarks = fit_har_benchmarks(train, test)

idata, student_samples = fit_bayesian_har(
    train,
    test,
    likelihood="student",
    draws=1000,
    tune=500,
    chains=2,
)

rv_true = test["rv_forward_5"].to_numpy()
evaluate_posterior_predictive(test[TARGET].to_numpy(), student_samples, rv_true)
```

## Next Statistical Steps

1. Compare Normal vs Student-t Bayesian HAR with posterior predictive checks.
2. Add VIX as an exogenous predictor, but evaluate whether it improves QLIKE.
3. Add jump/regime indicators only after the baseline Bayesian HAR is stable.
4. Report calibration: 80% and 95% interval coverage, not only point error.
5. Keep the model interpretable before adding more complex stochastic-volatility
   machinery.

## Repo Hygiene

Do not commit virtual environments, raw cached data, generated outputs, or large
notebook outputs. The remote `functions` branch appears to contain a committed
virtual environment; future work should stay on a clean branch from `main`.
