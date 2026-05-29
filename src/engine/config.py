import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
FIGURES_DIR = PROJECT_ROOT / "figures"
DB_PATH = DATA_DIR / "risk_system.db"
RISK_STATE_FILE = DATA_DIR / "risk_state.npz"
LIMITS_FILE = DATA_DIR / "risk_limits.json"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Assets Configuration
TICKERS = ["SPY", "AAPL", "GLD"]
DEFAULT_WEIGHTS = [0.4, 0.4, 0.2]
INITIAL_PORTFOLIO_VALUE = 1_000_000.0

# Market assumptions (for fallback generation)
FALLBACK_MU = [0.08, 0.12, 0.05]
FALLBACK_SIGMA = [0.15, 0.25, 0.10]
FALLBACK_CORR = [
    [1.0, 0.6, -0.1],
    [0.6, 1.0, 0.1],
    [-0.1, 0.1, 1.0]
]

# Risk Configuration
CONFIDENCE_LEVELS = [0.95, 0.99]
HORIZONS = [1, 10]  # in days
DISTRIBUTION = "Normal"  # or "Student-t"
STUDENT_T_DF = 4.0

# Liquidity (Bid-Ask Spread estimates)
BID_ASK_SPREADS = [0.0002, 0.0005, 0.0003] # SPY, AAPL, GLD

# Quantum Configuration
QUBITS_PER_ASSET = 4  # Total = 12
DEFAULT_SHOTS = 10000
FAST_SHOTS = 2000
USE_NOISE = False
NOISE_PROBABILITY = 0.01

# Training/Calibration
CALIBRATION_EPOCHS = 20
LEARNING_RATE = 0.1

# Backtesting Configuration
HISTORY_DAYS = 500
BACKTEST_WINDOW = 250

# Risk Limits (calibrated to annual horizon portfolio VaR)
# With portfolio vol ~14% annually, 95% VaR ~ 0.16-0.22
LIMITS = {
    "VaR_95": 0.22,
    "CVaR_95": 0.28
}
