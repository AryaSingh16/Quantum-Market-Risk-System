# Quantum Monte Carlo Portfolio Market Risk(v2)

This project is a Quantum-enhanced Monte Carlo system for estimating portfolio Value-at-Risk (VaR) and Conditional Value-at-Risk (CVaR), benchmarked against classical Monte Carlo under identical assumptions.

## Why this Project?

Modern banks and asset managers must compute portfolio VaR and CVaR every day under strict regulatory and time constraints. This requires running large-scale Monte Carlo simulations that can be computationally expensive, especially for high-dimensional portfolios or intraday recalculations.

This project explores how quantum sampling can plug into an existing market-risk stack as a drop-in scenario generator. The goal is not to replace classical infrastructure, but to show that quantum devices can produce risk numbers (VaR, CVaR, backtesting exceptions) that are statistically consistent with classical engines while potentially scaling better as hardware improves.

Concretely, the project addresses the problem of:
- Generating large numbers of plausible market scenarios for portfolio risk.
- Aggregating these scenarios into standard regulatory metrics (VaR/CVaR).
- Checking whether daily risk limits and Basel-style backtesting constraints are respected.

--- 

## Key Features

- **Quantum scenario generation** using PennyLane Hadamard sampling for bitstring-based paths.
- **Classical Monte Carlo benchmarking** under identical drift, volatility, and horizon assumptions.
- **Portfolio VaR & CVaR aggregation** with correlation-aligned multi-asset portfolios.
- **Volatility stress testing** across a configurable volatility grid (e.g., 0.1–0.4).
- **Risk limit governance** with PASS / WARNING / BREACH flags based on daily VaR.
- **Basel-style VaR backtesting** using exception counts over many scenarios.
- **Confidence-level stability analysis** with 95% as the default confidence level.

## Architecture

| Stage           | Component              | Purpose                                   |
|-----------------|------------------------|-------------------------------------------|
| **Input**       | Quantum Sampler        | Hadamard-based scenario generation        |
| **Mapping**     | Scenario Mapping       | Bitstrings → Gaussian shocks → returns    |
| **Core**        | Risk Metrics           | VaR / CVaR computation                    |
| **Aggregation** | Portfolio Aggregation  | Weighted multi-asset portfolio returns    |
| **Output**      | Limits & Backtesting   | Risk limits, exception counts, stability  |

---

## Installation and Running of project

### File Structure
├── src/
│ ├── scenario_portfolio_risk.py # Core quantum vs classical VaR/CVaR + portfolio risk
│ ├── risk_limits.py # Daily risk limits and status flags
│ └── backtesting.py # Basel-style portfolio backtesting
├── data/
│ └── risk_state.npz # Saved portfolio results (ignored by Git)
├── figures/ # Generated plots 
├── requirements.txt # Python dependencies
└── .gitignore # e.g., pycache/, /data/*.npz

### Prerequisites

Clone the repository, then install dependencies from `requirements.txt`:

pip install -r requirements.txt

Make sure Python and system packages for PennyLane, SciPy, Matplotlib, and NumPy are available on your machine.

### Run Analysis

python src/scenario_portfolio_risk.py # Single-asset + portfolio baseline quantum vs classical
python src/risk_limits.py # Daily risk limits and PASS/WARNING/BREACH checks
python src/backtesting.py # Basel-style portfolio backtesting and exceptions

--- 

## Results Overview

The following numbers are representative outputs from a 50,000-scenario run at 95% confidence:

| Component                 | Quantum          | Classical        |
|---------------------------|------------------|------------------|
| Single-asset VaR (95%)    | 0.2519           | 0.2588           |
| Single-asset CVaR (95%)   | 0.2988           | 0.3177           |
| Portfolio VaR (95%)       | 0.2574           | 0.2629           |
| Portfolio CVaR (95%)      | 0.3043           | 0.3207           |
| Backtest exceptions (95%) | 2272 / 50000     | 2500 / 50000     |

These results show that quantum and classical risk metrics align within typical Monte Carlo sampling error for 50,000 paths, and that exception rates are close to the theoretical 5% expected for a 95% VaR model.

## Why This Matters

This project demonstrates how quantum sampling can be integrated into real-world market-risk workflows without replacing existing classical infrastructure. Quantum methods supply alternative scenario generation while classical components still handle aggregation, limits, governance, and regulatory reporting, making the architecture realistic for bank risk desks.

---
## Credits

Project design, implementation, and experiments by Arya.  
Built using PennyLane, NumPy, SciPy, and Matplotlib for quantum circuits, numerical routines, and visualization.
