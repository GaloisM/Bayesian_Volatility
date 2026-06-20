# Bayesian Volatility

This repository contains a notebook-based analysis of realized-volatility
forecasting. The project starts from simple HAR regressions and then moves
towards Bayesian models and high-volatility warning signals.

The main notebook is:

- `bayesian_volatility_clean.ipynb`

The original exploratory notebook is kept as:

- `prep_data.ipynb`

## Main Idea

Realized volatility is difficult to forecast as an exact point value. On the raw
variance scale, the series is dominated by sharp spikes and heavy-tailed shocks.
Simple linear HAR models are therefore expected to be limited.

However, after moving to the log-volatility scale, the HAR structure captures a
smoother and more persistent volatility component. The remaining sudden
deviations motivate a Bayesian model with predictive uncertainty, especially a
Student-t likelihood.

The final goal is not only point prediction. We also use the Bayesian posterior
predictive distribution to build warning signals for high-volatility periods.

## Target

Daily realized variance is defined as:

```text
RV_t = log(S_t / S_{t-1})^2
```

The prediction target is the mean realized variance over the next five trading
days:

```text
RV_forward_5 = mean(RV_{t+1}, ..., RV_{t+5})
```

Most of the main regression analysis is performed on:

```text
log(RV_forward_5)
```

## Notebook Flow

The clean notebook follows the same research path as the original `prep_data`
notebook, but with the code and interpretation organized more clearly:

1. Download S&P 500, NASDAQ, and VIX data.
2. Construct daily returns and realized variance.
3. Fit a basic HAR model on raw realized variance.
4. Check whether Ridge regularization helps.
5. Add a jump-regime HAR extension.
6. Inspect whether jump-regime coefficients carry information.
7. Move to a log-HAR specification.
8. Compare OLS, Ridge, and naive benchmarks.
9. Fit Bayesian HAR models with Normal and Student-t likelihoods.
10. Evaluate posterior predictive intervals.
11. Build high-volatility warning signals.

## Warning Framework

The warning framework reformulates the task. Instead of asking whether the model
can predict each volatility spike exactly, we ask whether it can identify periods
where high volatility becomes plausible.

High-volatility events are defined using a threshold, for example the 80th
percentile of realized `RV_forward_5`.

The Bayesian model can then generate warnings using:

- posterior predictive mean,
- upper predictive bounds,
- or posterior probability of crossing the high-volatility threshold.

This makes the evaluation more useful for risk management, where recall,
precision, and the number of warnings are often more informative than point
forecast error alone.

## Setup

Use Python 3.12. The tested setup is Python 3.12 with the dependencies from
`requirements.txt`.

Clone the repository:

```bash
git clone https://github.com/GaloisM/Bayesian_Volatility.git
cd Bayesian_Volatility
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
.\run_jupyter.ps1
```

If PowerShell blocks local scripts, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_jupyter.ps1
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
sh run_jupyter.sh
```

Then open the main notebook:

```text
bayesian_volatility_clean.ipynb
```

The repository includes `data/prices_2010_2023.csv`, so the notebook can run
without downloading data from Yahoo Finance. If the file is removed, the data
cell will attempt to download the same period again and recreate it.

In JupyterLab, select the `Python (.venv Bayesian Volatility)` or `Python 3`
kernel from the local `.venv`.

## Metrics

The notebook reports:

- RMSE, MAE, and R2 on the log-volatility scale,
- RMSE, MAE, and R2 on the variance scale,
- QLIKE loss,
- posterior predictive interval coverage,
- warning precision, recall, F1 score, and number of warnings.

## Notes

Do not commit virtual environments, cached data, generated outputs, or large
notebook scratch files.
