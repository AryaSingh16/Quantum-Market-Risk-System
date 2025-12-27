import numpy as np
import matplotlib.pyplot as plt

data = np.load("data\risk_state.npz")

portfolio_returns_q = data["portfolio_returns_q"]
portfolio_returns_c = data["portfolio_returns_c"]
q_port_VaR = float(data["q_port_VaR"])
q_port_CVaR = float(data["q_port_CVaR"])
c_port_VaR = float(data["c_port_VaR"])
c_port_CVaR = float(data["c_port_CVaR"])

# -----------------------------
# Define risk limits 
# -----------------------------
LIMITS = {
    "VaR": 0.26,
    "CVaR": 0.32
}

# -----------------------------
# Breach logic
# -----------------------------
def check_breach(metric, limit):
    if metric > limit:
        return "BREACH"
    elif metric > 0.9 * limit:
        return "WARNING"
    else:
        return "PASS"

results = {
    "Quantum VaR": (q_port_VaR, check_breach(q_port_VaR, LIMITS["VaR"])),
    "Quantum CVaR": (q_port_CVaR, check_breach(q_port_CVaR, LIMITS["CVaR"])),
    "Classical VaR": (c_port_VaR, check_breach(c_port_VaR, LIMITS["VaR"])),
    "Classical CVaR": (c_port_CVaR, check_breach(c_port_CVaR, LIMITS["CVaR"]))
}

# -----------------------------
# Risk report
# -----------------------------
print("\n===== DAILY RISK LIMIT CHECK =====")
for k, (val, status) in results.items():
    print(f"{k:18s}: {val:.4f} | Status: {status}")

# -----------------------------
# Plot: Risk vs Limits
# -----------------------------
labels = list(results.keys())
values = [v[0] for v in results.values()]
limits = [
    LIMITS["VaR"], LIMITS["CVaR"],
    LIMITS["VaR"], LIMITS["CVaR"]
]

plt.figure(figsize=(9,5))
plt.bar(labels, values)
plt.plot(labels, limits, linestyle="--", label="Risk Limit", color="red")
plt.ylabel("Risk Value")
plt.title("Daily Risk Metrics vs Limits")
plt.xticks(rotation=20)
plt.legend()
plt.tight_layout()
plt.savefig("figures/risk_limits.png", dpi=300)
plt.show()

