import os
import numpy as np
import matplotlib.pyplot as plt
import json

from src.engine.config import LIMITS, LIMITS_FILE
from src.engine.database import init_db

def check_breach(metric, limit):
    if metric > limit:
        return "BREACH"
    elif metric > 0.9 * limit:
        return "WARNING"
    else:
        return "PASS"

def run_risk_limits():
    init_db()
    data = np.load(os.path.join("data", "risk_state.npz"))
    
    q_port_VaR = float(data["q_port_VaR"])
    q_port_CVaR = float(data["q_port_CVaR"])
    c_port_VaR = float(data["c_port_VaR"])
    c_port_CVaR = float(data["c_port_CVaR"])
    
    results = {
        "Quantum VaR": (q_port_VaR, check_breach(q_port_VaR, LIMITS["VaR_95"])),
        "Quantum CVaR": (q_port_CVaR, check_breach(q_port_CVaR, LIMITS["CVaR_95"])),
        "Classical VaR": (c_port_VaR, check_breach(c_port_VaR, LIMITS["VaR_95"])),
        "Classical CVaR": (c_port_CVaR, check_breach(c_port_CVaR, LIMITS["CVaR_95"]))
    }
    
    print("\n===== DAILY RISK LIMIT CHECK =====")
    for k, (val, status) in results.items():
        print(f"{k:18s}: {val:.4f} | Status: {status}")
        
    labels = list(results.keys())
    values = [v[0] for v in results.values()]
    limits = [LIMITS["VaR_95"], LIMITS["CVaR_95"], LIMITS["VaR_95"], LIMITS["CVaR_95"]]
    
    plt.figure(figsize=(9,5))
    plt.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#1f77b4', '#ff7f0e'])
    plt.plot(labels, limits, linestyle="--", label="Risk Limit", color="red", linewidth=2)
    plt.ylabel("Risk Value (Loss %)")
    plt.title("Daily Risk Metrics vs Calibrated Limits")
    plt.xticks(rotation=20)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/risk_limits.png", dpi=300)
    plt.close()
    
    limits_summary = {k: status for k, (_, status) in results.items()}
    with open(LIMITS_FILE, "w") as f:
        json.dump(limits_summary, f, indent=2)
        
    print("Risk limits check completed.")
    return limits_summary

if __name__ == "__main__":
    run_risk_limits()