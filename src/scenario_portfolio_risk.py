import pennylane as qml
from pennylane import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# -----------------------------
# Base parameters
# -----------------------------
S0 = 100.0
mu = 0.05
sigma_base = 0.2
T = 1.0
confidence = 0.95

n_qubits = 6
shots = 50_000

# -----------------------------
# Quantum device
# -----------------------------
dev = qml.device("default.qubit", wires=n_qubits, shots=shots)

@qml.qnode(dev)
def quantum_sampler():
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
    return qml.sample()

# -----------------------------
# Mapping
# -----------------------------
def bitstring_to_return(bitstring, sigma):
    z_int = sum(bit * (2 ** i) for i, bit in enumerate(bitstring))
    u = (z_int + 0.5) / (2**n_qubits)
    z = norm.ppf(u)
    ST = S0 * np.exp((mu - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    return (ST - S0) / S0

# -----------------------------
# Quantum sampling
# -----------------------------
samples = quantum_sampler()
returns_q = np.array([bitstring_to_return(s, sigma_base) for s in samples])

# -----------------------------
# Classical sampling
# -----------------------------
Z = np.random.normal(0, 1, shots)
prices_c = S0 * np.exp((mu - 0.5 * sigma_base**2) * T + sigma_base * np.sqrt(T) * Z)
returns_c = (prices_c - S0) / S0

# -----------------------------
# Risk metrics
# -----------------------------
def VaR_CVaR(returns, alpha):
    var = -np.percentile(returns, (1 - alpha) * 100)
    cvar = -returns[returns <= -var].mean()
    return var, cvar

if __name__ == "__main__":
    q_VaR, q_CVaR = VaR_CVaR(returns_q, confidence)
    c_VaR, c_CVaR = VaR_CVaR(returns_c, confidence)

    print("===== Risk Metrics (95%) =====")
    print(f"Quantum VaR  : {q_VaR:.4f} | Quantum CVaR  : {q_CVaR:.4f}")
    print(f"Classical VaR: {c_VaR:.4f} | Classical CVaR: {c_CVaR:.4f}")

    # -----------------------------
    # Plot 1: Distribution + VaR/CVaR
    # -----------------------------
    plt.figure(figsize=(8,5))
    plt.hist(returns_c, bins=50, density=True, alpha=0.6, label="Classical")
    plt.hist(returns_q, bins=50, density=True, alpha=0.6, label="Quantum")

    plt.axvline(-c_VaR, linestyle="--", label="Classical VaR")
    plt.axvline(-q_VaR, linestyle="--", label="Quantum VaR", color="red")
    plt.axvline(-c_CVaR, linestyle=":", label="Classical CVaR")
    plt.axvline(-q_CVaR, linestyle=":", label="Quantum CVaR", color="red")

    plt.xlabel("Returns")
    plt.ylabel("Density")
    plt.title("Quantum vs Classical Risk Distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/distribution.png", dpi=300)
    plt.show()


    # -----------------------------
    # Plot 2: Stress Test (Volatility)
    # -----------------------------
    vol_grid = np.linspace(0.1, 0.4, 8)
    q_var_stress = []
    c_var_stress = []

    for vol in vol_grid:
        q_returns = np.array([bitstring_to_return(s, vol) for s in samples])
        q_var, _ = VaR_CVaR(q_returns, confidence)
        q_var_stress.append(q_var)

        Z = np.random.normal(0, 1, shots)
        ST = S0 * np.exp((mu - 0.5 * vol**2) * T + vol * np.sqrt(T) * Z)
        c_returns = (ST - S0) / S0
        c_var, _ = VaR_CVaR(c_returns, confidence)
        c_var_stress.append(c_var)

    plt.figure(figsize=(8,5))
    plt.plot(vol_grid, q_var_stress, marker="o", label="Quantum VaR")
    plt.plot(vol_grid, c_var_stress, marker="s", label="Classical VaR")
    plt.xlabel("Volatility")
    plt.ylabel("VaR (95%)")
    plt.title("Stress Test: Volatility Sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/stress_test.png", dpi=300)
    plt.show()

    # -----------------------------

    # ============================================================
    # Portfolio Risk Aggregation 
    # ============================================================

    # Portfolio definition
    weights = np.array([0.4, 0.35, 0.25])
    sigmas = np.array([0.2, 0.25, 0.15])

    # -----------------------------
    # Quantum portfolio returns
    # -----------------------------
    portfolio_returns_q = []

    for s in samples:
        asset_returns = [
            bitstring_to_return(s, sigmas[i]) for i in range(len(weights))
        ]
        portfolio_returns_q.append(np.dot(weights, asset_returns))

    portfolio_returns_q = np.array(portfolio_returns_q)

    q_port_VaR, q_port_CVaR = VaR_CVaR(portfolio_returns_q, confidence)

    # -----------------------------
    # Classical portfolio returns
    # -----------------------------
    Z_shared = np.random.normal(0, 1, shots)
    portfolio_returns_c = []

    for z in Z_shared:
        asset_returns = []
        for j in range(len(weights)):
            ST = S0 * np.exp(
                (mu - 0.5 * sigmas[j]**2) * T +
                sigmas[j] * np.sqrt(T) * z   
            )
            asset_returns.append((ST - S0) / S0)

        portfolio_returns_c.append(np.dot(weights, asset_returns))

    portfolio_returns_c = np.array(portfolio_returns_c)

    c_port_VaR, c_port_CVaR = VaR_CVaR(portfolio_returns_c, confidence)

    # -----------------------------
    # Portfolio results
    # -----------------------------
    print("\n===== PORTFOLIO RISK (95%) =====")
    print(f"Quantum Portfolio VaR  : {q_port_VaR:.4f}")
    print(f"Quantum Portfolio CVaR : {q_port_CVaR:.4f}")
    print(f"Classical Portfolio VaR: {c_port_VaR:.4f}")
    print(f"Classical Portfolio CVaR: {c_port_CVaR:.4f}")
    print(f"VaR Error              : {abs(q_port_VaR - c_port_VaR):.4f}")
    print(f"CVaR Error             : {abs(q_port_CVaR - c_port_CVaR):.4f}")

    np.savez(
        "data\risk_state.npz",
        portfolio_returns_q=portfolio_returns_q,
        portfolio_returns_c=portfolio_returns_c,
        q_port_VaR=q_port_VaR,
        q_port_CVaR=q_port_CVaR,
        c_port_VaR=c_port_VaR,
        c_port_CVaR=c_port_CVaR
    )
    # -----------------------------
