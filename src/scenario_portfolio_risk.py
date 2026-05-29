import os
import numpy as np
import matplotlib.pyplot as plt

from src.engine.config import TICKERS, DEFAULT_WEIGHTS, INITIAL_PORTFOLIO_VALUE, FAST_SHOTS, DEFAULT_SHOTS, QUBITS_PER_ASSET
from src.engine.quantum_engine import QuantumRiskEngine
from src.engine.risk_metrics import calculate_var_cvar, calculate_marginal_var, calculate_component_var
from src.engine.backtester import get_historical_data
from src.engine.database import init_db, log_execution

def run_scenario_risk(mode="FULL"):
    init_db()
    print(f"Running Scenario Portfolio Risk in {mode} mode...")
    
    shots = FAST_SHOTS if mode == "FAST" else DEFAULT_SHOTS
    
    # 1. Fetch historical data to calibrate correlation and volatility
    returns_history = get_historical_data()
    
    mu = np.mean(returns_history, axis=0) * 252
    sigma = np.std(returns_history, axis=0) * np.sqrt(252)
    corr = np.corrcoef(returns_history, rowvar=False)
    
    # Ensure correlation matrix is positive semi-definite
    min_eig = np.min(np.real(np.linalg.eigvals(corr)))
    if min_eig < 0:
        corr -= 1.1 * min_eig * np.eye(*corr.shape)
        
    weights = np.array(DEFAULT_WEIGHTS)
    
    # 2. Quantum Engine Setup & Calibration
    q_engine = QuantumRiskEngine(num_assets=len(TICKERS), qubits_per_asset=QUBITS_PER_ASSET, shots=shots)
    q_engine.calibrate(corr)
    
    # 3. Simulate Scenarios (pass correlation matrix, NOT covariance)
    q_returns = q_engine.generate_correlated_returns(mu, sigma, corr)
    c_returns = q_engine.generate_classical_returns(mu, sigma, corr)
    
    q_port_returns = np.dot(q_returns, weights)
    c_port_returns = np.dot(c_returns, weights)
    
    # 4. Calculate Risk Metrics
    q_var, q_cvar = calculate_var_cvar(q_port_returns, 0.95)
    c_var, c_cvar = calculate_var_cvar(c_port_returns, 0.95)
    
    print("\n===== PORTFOLIO RISK (95%) =====")
    print(f"Quantum Portfolio VaR  : {q_var:.4f}")
    print(f"Quantum Portfolio CVaR : {q_cvar:.4f}")
    print(f"Classical Portfolio VaR: {c_var:.4f}")
    print(f"Classical Portfolio CVaR: {c_cvar:.4f}")
    
    # Calculate Marginal VaR
    q_mvar = calculate_marginal_var(q_returns, q_port_returns)
    c_mvar = calculate_marginal_var(c_returns, c_port_returns)
    q_comp_var = calculate_component_var(q_mvar, weights)
    
    # 5. Persist State
    np.savez(
        os.path.join("data", "risk_state.npz"),
        portfolio_returns_q=q_port_returns,
        portfolio_returns_c=c_port_returns,
        q_port_VaR=q_var,
        q_port_CVaR=q_cvar,
        c_port_VaR=c_var,
        c_port_CVaR=c_cvar,
        q_mvar=q_mvar,
        q_comp_var=q_comp_var,
        tickers=TICKERS
    )
    
    # Log Execution
    metrics = {
        "quantum_var_95": float(q_var),
        "classical_var_95": float(c_var),
        "quantum_cvar_95": float(q_cvar),
        "classical_cvar_95": float(c_cvar)
    }
    log_execution(mode, "SUCCESS", metrics)
    
    # 6. Generate Plots
    plt.figure(figsize=(8,5))
    plt.hist(c_port_returns, bins=50, density=True, alpha=0.6, label="Classical")
    plt.hist(q_port_returns, bins=50, density=True, alpha=0.6, label="Quantum")
    plt.axvline(-c_var, linestyle="--", label="Classical VaR")
    plt.axvline(-q_var, linestyle="--", label="Quantum VaR", color="red")
    plt.axvline(-c_cvar, linestyle=":", label="Classical CVaR")
    plt.axvline(-q_cvar, linestyle=":", label="Quantum CVaR", color="red")
    plt.xlabel("Returns")
    plt.ylabel("Density")
    plt.title("Quantum vs Classical Portfolio Risk Distribution")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig("figures/distribution.png", dpi=300)
    plt.close()
    
    print("Scenario generation completed.")
    return metrics

if __name__ == "__main__":
    mode = os.getenv("QMC_MODE", "FULL")
    run_scenario_risk(mode)
