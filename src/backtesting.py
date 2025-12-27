import numpy as np
import matplotlib.pyplot as plt
from src.scenario_portfolio_risk import VaR_CVaR

data = np.load("data\risk_state.npz")

portfolio_returns_q = data["portfolio_returns_q"]
portfolio_returns_c = data["portfolio_returns_c"]
q_port_VaR = float(data["q_port_VaR"])
q_port_CVaR = float(data["q_port_CVaR"])
c_port_VaR = float(data["c_port_VaR"])
c_port_CVaR = float(data["c_port_CVaR"])

# ============================================================
# Basel-Style Backtesting
# ============================================================

def backtest_VaR(returns, VaR):
    # Count days where loss exceeded VaR
    losses = -returns
    exceptions = losses > VaR
    return exceptions.sum(), len(returns)

# Backtesting on portfolio returns
q_ex, q_total = backtest_VaR(portfolio_returns_q, q_port_VaR)
c_ex, c_total = backtest_VaR(portfolio_returns_c, c_port_VaR)

print("\n===== BASEL BACKTESTING (PORTFOLIO) =====")
print(f"Quantum Exceptions  : {q_ex}/{q_total} ({q_ex/q_total:.2%})")
print(f"Classical Exceptions: {c_ex}/{c_total} ({c_ex/c_total:.2%})")


plt.figure(figsize=(6,4))
plt.bar(
    ["Quantum", "Classical"],
    [q_ex/q_total, c_ex/c_total]
)
plt.axhline(0.05, linestyle="--", label="Expected 5%", color="green")
plt.ylabel("Exception Rate")
plt.title("Basel Backtesting: VaR Exceptions")
plt.legend()
plt.tight_layout()
plt.savefig("figures/backtesting.png", dpi=300)
plt.show()


# ============================================================
# Confidence Sweep
# ============================================================

conf_levels = np.linspace(0.90, 0.99, 10)
q_vars = []
c_vars = []

for alpha in conf_levels:
    qv, _ = VaR_CVaR(portfolio_returns_q, alpha)
    cv, _ = VaR_CVaR(portfolio_returns_c, alpha)
    q_vars.append(qv)
    c_vars.append(cv)

plt.figure(figsize=(8,5))
plt.plot(conf_levels, q_vars, marker="o", label="Quantum VaR")
plt.plot(conf_levels, c_vars, marker="s", label="Classical VaR")
plt.xlabel("Confidence Level")
plt.ylabel("Portfolio VaR")
plt.title("Confidence-Level Stability Check")
plt.legend()
plt.tight_layout()
plt.savefig("figures/confidence.png", dpi=300)
plt.show()

