import numpy as np
import pytest
from src.engine.risk_metrics import calculate_var_cvar, calculate_l_var, calculate_marginal_var
from src.engine.quantum_engine import QuantumRiskEngine
from src.engine.config import DEFAULT_WEIGHTS

def test_var_cvar_calculation():
    # Simple normal distribution mock
    np.random.seed(42)
    returns = np.random.normal(0, 0.1, 10000)
    
    var, cvar = calculate_var_cvar(returns, confidence_level=0.95)
    
    # Check that VaR is positive (it's a loss metric) and CVaR > VaR
    assert var > 0
    assert cvar > 0
    assert cvar > var
    
    # Theoretical 95% VaR for N(0, 0.1^2) is approx 0.1645
    assert np.isclose(var, 0.1645, atol=0.01)

def test_l_var_calculation():
    var = 0.05
    weights = np.array([0.5, 0.5])
    prices = np.array([100.0, 50.0])
    spreads = np.array([0.01, 0.02])
    
    # liquidation cost = sum(w * P * S / 2)
    # cost1 = 0.5 * 100 * 0.01 / 2 = 0.25
    # cost2 = 0.5 * 50 * 0.02 / 2 = 0.25
    # Total cost = 0.5
    # Total port value = 0.5*100 + 0.5*50 = 75
    # Cost pct = 0.5 / 75 = 0.006666...
    
    l_var = calculate_l_var(var, weights, prices, spreads)
    assert l_var > var
    assert np.isclose(l_var, 0.05 + 0.006666, atol=0.001)

def test_quantum_engine_initialization():
    engine = QuantumRiskEngine(num_assets=2, qubits_per_asset=2, shots=100)
    assert engine.total_qubits == 4
    
    shocks = engine.generate_independent_shocks()
    assert shocks.shape == (100, 2)

def test_cholesky_correlation():
    engine = QuantumRiskEngine(num_assets=2, qubits_per_asset=2, shots=1000)
    mu = [0.0, 0.0]
    sigma = [0.1, 0.2]
    # Perfect correlation
    corr = np.array([
        [1.0, 1.0],
        [1.0, 1.0]
    ])
    
    returns = engine.generate_classical_returns(mu, sigma, corr)
    
    # Standardize returns
    r1 = returns[:, 0] / 0.1
    r2 = returns[:, 1] / 0.2
    
    # Check empirical correlation is close to 1.0
    empirical_corr = np.corrcoef(r1, r2)[0, 1]
    assert np.isclose(empirical_corr, 1.0, atol=0.05)
