import os
import numpy as np
import matplotlib.pyplot as plt

from src.engine.config import TICKERS, DEFAULT_WEIGHTS, FAST_SHOTS
from src.engine.backtester import get_historical_data
from src.engine.quantum_engine import QuantumRiskEngine
from src.engine.risk_metrics import calculate_var_cvar

def run_stress_testing(mode="FULL"):
    print("Running volatility stress testing sensitivity analysis...")
    
    # Define volatility shocks (10% to 40%)
    vol_levels = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
    
    # 1. Fetch historical data for correlation structure
    returns_history = get_historical_data()
    corr = np.corrcoef(returns_history, rowvar=False)
    
    # Ensure positive semi-definite
    min_eig = np.min(np.real(np.linalg.eigvals(corr)))
    if min_eig < 0:
        corr -= 1.1 * min_eig * np.eye(*corr.shape)
        
    weights = np.array(DEFAULT_WEIGHTS)
    
    # Use fewer shots for stress testing to keep it fast
    shots = 1000 if mode == "FAST" else 2000
    
    q_vars = []
    c_vars = []
    
    # We calibrate the quantum engine once
    q_engine = QuantumRiskEngine(num_assets=len(TICKERS), shots=shots)
    q_engine.calibrate(corr)
    
    # We use a fixed mean of zero to isolate the volatility impact (zero-drift assumption)
    mu_zero = np.zeros(len(TICKERS))
    
    for vol in vol_levels:
        # Create a volatility vector where assets scale with base volatility
        sigma = np.array([vol * 0.8, vol * 1.3, vol * 0.5])
        
        # Quantum
        q_returns = q_engine.generate_correlated_returns(mu_zero, sigma, corr)
        q_port_returns = np.dot(q_returns, weights)
        q_var, _ = calculate_var_cvar(q_port_returns, 0.95)
        q_vars.append(q_var)
        
        # Classical
        c_returns = q_engine.generate_classical_returns(mu_zero, sigma, corr)
        c_port_returns = np.dot(c_returns, weights)
        c_var, _ = calculate_var_cvar(c_port_returns, 0.95)
        c_vars.append(c_var)
        
    # Plot results
    plt.figure(figsize=(8, 5))
    plt.plot(vol_levels * 100, np.array(q_vars) * 100, marker='o', label="Quantum VaR (95%)", color="red", linewidth=2)
    plt.plot(vol_levels * 100, np.array(c_vars) * 100, marker='s', label="Classical VaR (95%)", color="blue", linewidth=2, linestyle='--')
    plt.xlabel("Base Market Volatility (%)")
    plt.ylabel("Portfolio VaR (%)")
    plt.title("Volatility Sensitivity Analysis (Stress Testing)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig("figures/stress_test.png", dpi=300)
    plt.close()
    print("Stress testing analysis complete.")

if __name__ == "__main__":
    run_stress_testing()
