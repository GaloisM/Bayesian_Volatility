"""Statistical models for realized-volatility forecasting.

This file is intentionally small. The project is a research notebook plus a
minimal reusable statistical core, not a production application.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


HAR_FEATURES = ["log_rv_lag_1", "log_rv_mean_5", "log_rv_mean_22"]
TARGET = "log_rv_forward_5"


def make_har_dataset(
    close: pd.Series,
    horizon: int = 5,
    eps: float = 1e-12,
) -> pd.DataFrame:
    """Create a leakage-safe HAR dataset from close prices.

    RV is proxied by squared daily log returns. The target is the average
    realized variance over the next ``horizon`` trading days.
    """
    if horizon < 1:
        raise ValueError("horizon must be at least 1")

    df = close.to_frame("close").copy()
    df["ret_1d"] = np.log(df["close"] / df["close"].shift(1))
    df["rv_1d"] = df["ret_1d"] ** 2

    past_rv = df["rv_1d"].shift(1)
    df["rv_lag_1"] = past_rv
    df["rv_mean_5"] = past_rv.rolling(5).mean()
    df["rv_mean_22"] = past_rv.rolling(22).mean()

    df[f"rv_forward_{horizon}"] = sum(
        df["rv_1d"].shift(-step) for step in range(1, horizon + 1)
    ) / horizon

    df["log_rv_lag_1"] = np.log(df["rv_lag_1"] + eps)
    df["log_rv_mean_5"] = np.log(df["rv_mean_5"] + eps)
    df["log_rv_mean_22"] = np.log(df["rv_mean_22"] + eps)
    df["log_rv_forward_5"] = np.log(df[f"rv_forward_{horizon}"] + eps)

    return df[HAR_FEATURES + [TARGET, f"rv_forward_{horizon}"]].dropna()


def train_test_split_time(
    data: pd.DataFrame,
    train_fraction: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological split; no shuffling for time series."""
    split = int(len(data) * train_fraction)
    if split <= 0 or split >= len(data):
        raise ValueError("train_fraction leaves an empty train or test set")
    return data.iloc[:split], data.iloc[split:]


def fit_har_benchmarks(
    train: pd.DataFrame,
    test: pd.DataFrame,
    alpha: float = 1.0,
) -> dict[str, np.ndarray]:
    """Fit OLS HAR and Ridge HAR on log realized variance."""
    x_train = train[HAR_FEATURES]
    y_train = train[TARGET]
    x_test = test[HAR_FEATURES]

    ols = LinearRegression().fit(x_train, y_train)
    ridge = Pipeline(
        [
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=alpha)),
        ]
    ).fit(x_train, y_train)

    return {
        "OLS HAR": ols.predict(x_test),
        "Ridge HAR": ridge.predict(x_test),
    }


def fit_bayesian_har(
    train: pd.DataFrame,
    test: pd.DataFrame,
    likelihood: str = "student",
    draws: int = 1000,
    tune: int = 500,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> tuple[object, np.ndarray]:
    """Fit Bayesian HAR and return posterior predictive samples on log(RV).

    ``likelihood='student'`` is the preferred model because volatility forecast
    errors are heavy-tailed. Use ``likelihood='normal'`` as a simpler reference.
    """
    import pymc as pm

    x_scaler = StandardScaler()
    y_scaler = StandardScaler()

    x_train = x_scaler.fit_transform(train[HAR_FEATURES])
    x_test = x_scaler.transform(test[HAR_FEATURES])
    y_train = y_scaler.fit_transform(train[[TARGET]]).ravel()

    coords = {"obs": np.arange(len(train)), "feature": HAR_FEATURES}
    with pm.Model(coords=coords) as model:
        x_data = pm.Data("x", x_train, dims=("obs", "feature"))
        y_data = pm.Data("y", y_train, dims="obs")

        alpha = pm.Normal("alpha", 0.0, 1.0)
        beta = pm.Normal("beta", 0.0, 1.0, dims="feature")
        sigma = pm.HalfNormal("sigma", 1.0)
        mu = pm.Deterministic("mu", alpha + pm.math.dot(x_data, beta), dims="obs")

        if likelihood == "normal":
            pm.Normal("obs_rv", mu=mu, sigma=sigma, observed=y_data, dims="obs")
        elif likelihood == "student":
            nu = pm.Deterministic("nu", pm.Exponential("nu_minus_2", 1 / 10) + 2)
            pm.StudentT(
                "obs_rv",
                nu=nu,
                mu=mu,
                sigma=sigma,
                observed=y_data,
                dims="obs",
            )
        else:
            raise ValueError("likelihood must be 'normal' or 'student'")

        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=random_seed,
        )

        pm.set_data({"x": x_test}, coords={"obs": np.arange(len(test))})
        ppc = pm.sample_posterior_predictive(
            idata,
            var_names=["obs_rv"],
            random_seed=random_seed,
        )

    samples_scaled = ppc.posterior_predictive["obs_rv"].values
    samples_scaled = samples_scaled.reshape(-1, samples_scaled.shape[-1])
    samples_log = y_scaler.inverse_transform(samples_scaled.reshape(-1, 1)).reshape(
        samples_scaled.shape
    )
    return idata, samples_log


def qlike(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-12) -> float:
    """QLIKE loss for variance forecasts; lower is better."""
    y_true = np.maximum(np.asarray(y_true), eps)
    y_pred = np.maximum(np.asarray(y_pred), eps)
    ratio = y_true / y_pred
    return float(np.mean(ratio - np.log(ratio) - 1))


def evaluate_log_forecast(
    y_true_log: np.ndarray,
    y_pred_log: np.ndarray,
    rv_true: np.ndarray,
) -> dict[str, float]:
    """Evaluate one point forecast on log and variance scales."""
    rv_pred = np.exp(y_pred_log)
    return {
        "rmse_log": float(np.sqrt(mean_squared_error(y_true_log, y_pred_log))),
        "mae_log": float(mean_absolute_error(y_true_log, y_pred_log)),
        "r2_log": float(r2_score(y_true_log, y_pred_log)),
        "rmse_rv": float(np.sqrt(mean_squared_error(rv_true, rv_pred))),
        "mae_rv": float(mean_absolute_error(rv_true, rv_pred)),
        "r2_rv": float(r2_score(rv_true, rv_pred)),
        "qlike": qlike(rv_true, rv_pred),
    }


def evaluate_posterior_predictive(
    y_true_log: np.ndarray,
    samples_log: np.ndarray,
    rv_true: np.ndarray,
) -> dict[str, float]:
    """Evaluate posterior predictive samples and interval calibration."""
    mean_log = samples_log.mean(axis=0)
    lower_80 = np.quantile(samples_log, 0.10, axis=0)
    upper_80 = np.quantile(samples_log, 0.90, axis=0)
    lower_95 = np.quantile(samples_log, 0.025, axis=0)
    upper_95 = np.quantile(samples_log, 0.975, axis=0)

    out = evaluate_log_forecast(y_true_log, mean_log, rv_true)
    out.update(
        {
            "coverage_80": interval_coverage(y_true_log, lower_80, upper_80),
            "coverage_95": interval_coverage(y_true_log, lower_95, upper_95),
            "width_80": float(np.mean(upper_80 - lower_80)),
            "width_95": float(np.mean(upper_95 - lower_95)),
        }
    )
    return out


def interval_coverage(
    y_true: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> float:
    y_true = np.asarray(y_true)
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


def high_vol_warning_table(
    rv_true: np.ndarray,
    forecast_rv: dict[str, np.ndarray],
    threshold: float,
) -> pd.DataFrame:
    """Evaluate high-volatility warning signals at a chosen RV threshold."""
    y_true = (np.asarray(rv_true) > threshold).astype(int)
    rows = []

    for name, values in forecast_rv.items():
        signal = (np.asarray(values) > threshold).astype(int)
        rows.append(
            {
                "signal": name,
                "precision": precision_score(y_true, signal, zero_division=0),
                "recall": recall_score(y_true, signal, zero_division=0),
                "f1": f1_score(y_true, signal, zero_division=0),
                "n_warnings": int(signal.sum()),
                "n_high_vol": int(y_true.sum()),
            }
        )

    return pd.DataFrame(rows)
