import numpy as np
import pandas as pd
import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from src.engine.config import TICKERS, HISTORY_DAYS, FALLBACK_MU, FALLBACK_SIGMA, FALLBACK_CORR

def get_historical_data(tickers=TICKERS, days=HISTORY_DAYS):
    """
    Fetches historical daily returns for the specified tickers.
    Falls back to a realistic multivariate normal mock generator if yfinance fails.
    """
    if YFINANCE_AVAILABLE:
        try:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=int(days * 1.5))
            
            raw = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
            
            # yfinance auto_adjust=True gives 'Close' as the adjusted close
            if "Close" in raw.columns:
                data = raw["Close"]
            elif isinstance(raw.columns, pd.MultiIndex):
                data = raw["Close"]
            else:
                data = raw
            
            data = data.dropna()
            returns = data.pct_change().dropna()
            
            if len(returns) > days:
                returns = returns.iloc[-days:]
            
            if len(returns) < 50:
                raise ValueError("Not enough data rows returned")
                
            return returns.values
        except Exception as e:
            print(f"yfinance failed: {e}. Falling back to mock data.")
            return generate_mock_history(days)
    else:
        print("yfinance not installed. Using mock data.")
        return generate_mock_history(days)

def generate_mock_history(days):
    """Generates a realistic mock history of daily returns using a multivariate normal"""
    mu = np.array(FALLBACK_MU) / 252.0  # Daily drift
    sigma = np.array(FALLBACK_SIGMA) / np.sqrt(252.0)  # Daily volatility
    corr = np.array(FALLBACK_CORR)
    
    # Construct covariance matrix
    cov = np.outer(sigma, sigma) * corr
    
    # Generate daily returns
    returns = np.random.multivariate_normal(mu, cov, size=days)
    return returns

def get_basel_status(exceptions, total_days):
    """
    Determines Basel Traffic Light Status based on VaR exceptions.
    Approximated for a 250-day window at 99% or 95% (typically Basel uses 99% for 250 days).
    """
    # Using the standard Basel 99% VaR over 250 days bounds:
    # Green: 0-4, Yellow: 5-9, Red: 10+
    if exceptions <= 4:
        return "GREEN"
    elif exceptions <= 9:
        return "YELLOW"
    else:
        return "RED"
