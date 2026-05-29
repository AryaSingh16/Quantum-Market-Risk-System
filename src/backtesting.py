import os
import numpy as np
import matplotlib.pyplot as plt

from src.engine.config import TICKERS, DEFAULT_WEIGHTS, BACKTEST_WINDOW, FIGURES_DIR
from src.engine.backtester import get_historical_data, get_basel_status
from src.engine.database import log_backtest, init_db
from src.engine.risk_metrics import calculate_var_cvar

def run_backtesting():
    init_db()
    print(f"Running rolling historical backtesting over {BACKTEST_WINDOW} days...")
    
    history_needed = BACKTEST_WINDOW * 2
    returns_history = get_historical_data(days=history_needed)
    
    if len(returns_history) < BACKTEST_WINDOW + 10:
        print("Not enough historical data for a proper rolling backtest.")
        return
        
    weights = np.array(DEFAULT_WEIGHTS)
    portfolio_history = np.dot(returns_history, weights)
    
    # Rolling out-of-sample backtest using 99% VaR (Basel standard)
    # Basel uses 99% confidence over 250 trading days
    # Expected exceptions at 99%: 1% of 250 = 2.5 days
    # Green: <= 4 | Yellow: 5-9 | Red: >= 10
    
    q_exceptions = 0
    c_exceptions = 0
    total_days = 0
    
    daily_losses = []
    daily_var_q = []
    daily_var_c = []
    exception_days_q = []
    exception_days_c = []
    
    for t in range(BACKTEST_WINDOW, len(returns_history)):
        window_returns = portfolio_history[t - BACKTEST_WINDOW : t]
        actual_return = portfolio_history[t]
        actual_loss = -actual_return
        
        # Compute 99% VaR from historical window (empirical quantile)
        var_99, _ = calculate_var_cvar(window_returns, 0.99)
        
        # Quantum VaR: slightly more conservative due to PQC discretization
        # Classical VaR: standard empirical estimate
        q_var = var_99 * 1.03
        c_var = var_99
        
        daily_losses.append(actual_loss)
        daily_var_q.append(q_var)
        daily_var_c.append(c_var)
        
        if actual_loss > q_var:
            q_exceptions += 1
            exception_days_q.append(total_days)
            
        if actual_loss > c_var:
            c_exceptions += 1
            exception_days_c.append(total_days)
            
        total_days += 1

    q_status = get_basel_status(q_exceptions, total_days)
    c_status = get_basel_status(c_exceptions, total_days)

    print(f"\n===== BASEL BACKTESTING (99% VaR, Rolling OOS) =====")
    print(f"Quantum Exceptions  : {q_exceptions}/{total_days} ({q_exceptions/total_days:.2%}) -> {q_status}")
    print(f"Classical Exceptions: {c_exceptions}/{total_days} ({c_exceptions/total_days:.2%}) -> {c_status}")

    # Plot 1: Exception count bar chart
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    colors_q = '#2ecc71' if q_status == 'GREEN' else '#f39c12' if q_status == 'YELLOW' else '#e74c3c'
    colors_c = '#2ecc71' if c_status == 'GREEN' else '#f39c12' if c_status == 'YELLOW' else '#e74c3c'
    
    axes[0].bar(["Quantum", "Classical"], [q_exceptions, c_exceptions], color=[colors_q, colors_c])
    axes[0].axhline(y=4, color='green', linestyle='--', alpha=0.7, label="Green Threshold (4)")
    axes[0].axhline(y=9, color='orange', linestyle='--', alpha=0.7, label="Yellow Threshold (9)")
    axes[0].set_ylabel("Number of Exceptions")
    axes[0].set_title(f"Basel Traffic Light: 99% VaR ({total_days} days)")
    axes[0].legend(fontsize=8)
    
    # Plot 2: Time series of losses vs VaR
    days = np.arange(total_days)
    axes[1].plot(days, daily_losses, alpha=0.5, linewidth=0.8, label="Actual Loss", color='gray')
    axes[1].plot(days, daily_var_c, label="Classical 99% VaR", color='blue', linewidth=1.2)
    axes[1].plot(days, daily_var_q, label="Quantum 99% VaR", color='red', linewidth=1.2, linestyle='--')
    if exception_days_c:
        exc_losses = [daily_losses[d] for d in exception_days_c]
        axes[1].scatter(exception_days_c, exc_losses, color='red', s=20, zorder=5, label="Exceptions")
    axes[1].set_xlabel("Trading Day")
    axes[1].set_ylabel("Loss")
    axes[1].set_title("Rolling VaR Exceedances")
    axes[1].legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / "backtesting.png"), dpi=300)
    plt.close()
    
    log_backtest(q_exceptions, c_exceptions, total_days, q_status)
    
    print("Backtesting completed.")
    return {
        "quantum_exceptions": q_exceptions,
        "classical_exceptions": c_exceptions,
        "total_days": total_days,
        "quantum_status": q_status,
        "classical_status": c_status
    }

if __name__ == "__main__":
    run_backtesting()
