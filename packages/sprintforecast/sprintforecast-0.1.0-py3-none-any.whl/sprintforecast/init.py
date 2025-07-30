from __future__ import annotations
import json, pathlib, typing as t, numpy as np, pandas as pd
from dataclasses import dataclass
from numpy.random import default_rng
from scipy import optimize, stats
rng = default_rng()

class ErrorDistribution:
    def sample(self, size: int = 1) -> np.ndarray: ...
    def logpdf(self, x: np.ndarray) -> np.ndarray: ...
    def to_dict(self) -> dict: ...
    @staticmethod
    def from_dict(d: dict) -> "ErrorDistribution": ...

@dataclass(frozen=True, slots=True)
class LogNormalError(ErrorDistribution):
    mu: float
    sigma: float
    def sample(self, size: int = 1) -> np.ndarray:
        return rng.lognormal(self.mu, self.sigma, size)
    def logpdf(self, x: np.ndarray) -> np.ndarray:
        return stats.lognorm(self.sigma, scale=np.exp(self.mu)).logpdf(x)
    def to_dict(self) -> dict:
        return {"type": "lognormal", "mu": self.mu, "sigma": self.sigma}
    @staticmethod
    def fit(data: np.ndarray) -> "LogNormalError":
        mu, sigma = np.mean(np.log(data)), np.std(np.log(data), ddof=1)
        return LogNormalError(mu, sigma)

@dataclass(frozen=True, slots=True)
class SkewTError(ErrorDistribution):
    xi: float
    omega: float
    alpha: float
    df: float
    def sample(self, size: int = 1) -> np.ndarray:
        return stats.skewt(self.df, self.alpha, loc=self.xi, scale=self.omega).rvs(size, random_state=rng)
    def logpdf(self, x: np.ndarray) -> np.ndarray:
        return stats.skewt(self.df, self.alpha, loc=self.xi, scale=self.omega).logpdf(x)
    def to_dict(self) -> dict:
        return {"type": "skewt", "xi": self.xi, "omega": self.omega, "alpha": self.alpha, "df": self.df}
    @staticmethod
    def fit(data: np.ndarray) -> "SkewTError":
        def nll(params):
            xi, omega, alpha, df = params
            if omega <= 0 or df <= 2: return np.inf
            return -np.sum(stats.skewt(df, alpha, loc=xi, scale=omega).logpdf(data))
        x0 = (np.median(data), np.std(data, ddof=1), 1.0, 6.0)
        res = optimize.minimize(nll, x0, method="Nelder-Mead")
        xi, omega, alpha, df = res.x
        return SkewTError(float(xi), float(omega), float(alpha), float(df))

def choose_error_family(residuals: np.ndarray) -> ErrorDistribution:
    q = np.percentile(residuals, [80, 90, 95])
    test = (q[2] - q[0]) / (q[1] - q[0])
    return SkewTError.fit(residuals) if test > 1.6 else LogNormalError.fit(residuals)

@dataclass(frozen=True, slots=True)
class Pert:
    o: float
    m: float
    p: float
    def alpha_beta(self) -> tuple[float, float]:
        a = 1 + 4 * (self.m - self.o) / (self.p - self.o)
        b = 1 + 4 * (self.p - self.m) / (self.p - self.o)
        return a, b
    def sample(self, size: int = 1) -> np.ndarray:
        a, b = self.alpha_beta()
        return self.o + (self.p - self.o) * rng.beta(a, b, size)

@dataclass(frozen=True, slots=True)
class CapacityPosterior:
    mu: float
    sigma: float
    def sample(self, size: int = 1) -> np.ndarray:
        return np.exp(rng.normal(self.mu, self.sigma, size))

def ni_gamma_posterior(history: np.ndarray, m0: float = 0, k0: float = 1, a0: float = 2, b0: float = 0.5) -> CapacityPosterior:
    n = len(history)
    mean = history.mean()
    var = history.var(ddof=1)
    k_n = k0 + n
    mu_n = (k0 * m0 + n * mean) / k_n
    a_n = a0 + n / 2
    b_n = b0 + 0.5 * (n * var + k0 * n * (mean - m0) ** 2 / k_n)
    sigma = np.sqrt(b_n / (a_n - 1))
    return CapacityPosterior(float(mu_n), float(sigma))

@dataclass(slots=True)
class SprintForecaster:
    error_dist: ErrorDistribution
    capacity_post: CapacityPosterior
    triads: pd.DataFrame
    paths: int = 10_000
    def simulate(self) -> np.ndarray:
        triad_objs = self.triads[["o", "m", "p"]].apply(lambda r: Pert(*r), axis=1).tolist()
        x_prior = np.vstack([t.sample(self.paths) for t in triad_objs]).T
        errs = self.error_dist.sample(x_prior.size).reshape(self.paths, -1)
        effort = np.exp(errs) * x_prior
        total = effort.sum(axis=1)
        cap = self.capacity_post.sample(self.paths)
        return total / cap
    def summary(self, sprint_hours: float) -> dict[str, t.Any]:
        t_complete = self.simulate()
        prob = (t_complete <= sprint_hours).mean()
        brier = prob * (1 - prob)
        a = np.abs(t_complete[:, None] - t_complete[None, :]).mean()
        b = 0.5 * np.abs(t_complete[:, None] - t_complete[None, :]).mean()
        crps = a - b
        pct = np.percentile(t_complete, [50, 80, 95])
        return {"p50": pct[0], "p80": pct[1], "p95": pct[2], "P_goal": prob, "Brier": brier, "CRPS": crps}

@dataclass(slots=True)
class MomentumModel:
    caps: np.ndarray
    hours_per_sprint: float
    def fit(self) -> tuple[float, float, float]:
        s = np.arange(1, len(self.caps) + 1)
        y = np.log(self.caps)
        b, a = np.polyfit(s, y, 1)
        resid = y - (a + b * s)
        tau = resid.std(ddof=1)
        return float(a), float(b), float(tau)
    def forecast(self, size: int = 1) -> np.ndarray:
        a, b, tau = self.fit()
        k = len(self.caps) + 1
        mean = a + b * k
        var = tau ** 2 + tau ** 2 / k
        return np.exp(rng.normal(mean, np.sqrt(var), size))
    def momentum(self) -> float:
        _, b, _ = self.fit()
        return float(np.exp(b * self.hours_per_sprint))

@dataclass(slots=True)
class IntakePlanner:
    ticket_pool: pd.DataFrame
    error_dist: ErrorDistribution
    next_capacity: np.ndarray
    paths: int = 10_000
    def ticket_size_samples(self) -> np.ndarray:
        triads = self.ticket_pool[["o", "m", "p"]].values
        idx = rng.integers(0, len(triads), self.paths)
        triad_objs = [Pert(*triads[i]) for i in idx]
        x = np.array([t.sample() for t in triad_objs]).flatten()
        e = self.error_dist.sample(self.paths)
        return np.exp(e) * x
    def plan(self, gamma: float = 0.8) -> dict[str, t.Any]:
        cap = rng.choice(self.next_capacity, self.paths)
        sizes = self.ticket_size_samples()
        counts = np.ones_like(cap, dtype=int)
        cum = sizes
        while True:
            add = self.ticket_size_samples()
            if (cum + add > cap).all(): break
            mask = cum + add <= cap
            cum[mask] += add[mask]
            counts[mask] += 1
        counts = counts.astype(int)
        n = np.quantile(counts, [0.5, 0.2, 0.05])
        target = np.max(np.where(np.sort(counts) >= np.quantile(counts, 1 - gamma)))
        return {"n50": n[0], "n80": n[1], "n95": n[2], "recommended": target}

def load_triads(path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(path).assign(o=lambda d: d["o"].astype(float), m=lambda d: d["m"].astype(float), p=lambda d: d["p"].astype(float))

def load_actuals(path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(path).assign(actual=lambda d: d["actual"].astype(float))

def residuals(df: pd.DataFrame) -> np.ndarray:
    mu = (df["o"] + 4 * df["m"] + df["p"]) / 6
    return np.log(df["actual"].values / mu.values)

def save_dist(d: ErrorDistribution, path: pathlib.Path):
    path.write_text(json.dumps(d.to_dict()))

def load_dist(path: pathlib.Path) -> ErrorDistribution:
    jd = json.loads(path.read_text())
    return LogNormalError.from_dict(jd) if jd["type"] == "lognormal" else SkewTError.from_dict(jd)

import typer
app = typer.Typer(add_completion=False)

@app.command()
def fit_error(triads: pathlib.Path, actuals: pathlib.Path, out: pathlib.Path):
    df = pd.concat([load_triads(triads), load_actuals(actuals)], axis=1)
    r = residuals(df)
    dist = choose_error_family(r)
    save_dist(dist, out)
    typer.echo(out)

@app.command()
def forecast(triads: pathlib.Path, capacity_hist: pathlib.Path, dist_file: pathlib.Path, sprint_hours: float = 80):
    triad_df = load_triads(triads)
    cap_hist = np.loadtxt(capacity_hist)
    cap_post = ni_gamma_posterior(np.log(cap_hist))
    dist = load_dist(dist_file)
    f = SprintForecaster(dist, cap_post, triad_df)
    res = f.summary(sprint_hours)
    typer.echo(json.dumps(res, indent=2))

@app.command()
def plan_intake(pool: pathlib.Path, capacity_hist: pathlib.Path, dist_file: pathlib.Path, hours_per_sprint: float = 80, gamma: float = 0.8):
    caps = np.loadtxt(capacity_hist)
    mom = MomentumModel(caps, hours_per_sprint)
    next_cap = mom.forecast(10_000)
    pool_df = load_triads(pool)
    dist = load_dist(dist_file)
    p = IntakePlanner(pool_df, dist, next_cap)
    res = p.plan(gamma)
    res["momentum"] = mom.momentum()
    typer.echo(json.dumps(res, indent=2))
