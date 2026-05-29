import numpy as np

def calculate_var_cvar(returns, confidence_level=0.95):
    """Calculates Value at Risk and Conditional Value at Risk"""
    var = -np.percentile(returns, (1 - confidence_level) * 100)
    cvar = -returns[returns <= -var].mean()
    return var, cvar

def calculate_l_var(var, weights, prices, spreads):
    """
    Liquidity-Adjusted VaR (L-VaR).
    Adds the cost of liquidating the position based on bid-ask spreads.
    """
    liquidation_cost = np.sum(weights * (prices * spreads / 2.0))
    # Normalized to percentage of total portfolio
    liquidation_cost_pct = liquidation_cost / np.sum(weights * prices)
    return var + liquidation_cost_pct

def calculate_marginal_var(asset_returns, portfolio_returns, confidence_level=0.95):
    """
    Calculates Marginal VaR (MVaR) for each asset.
    MVaR_i is approximated by the expected return of asset i given that the 
    portfolio return is close to the percentile threshold.
    We approximate this by taking the mean asset returns when portfolio returns 
    are close to the VaR threshold (within a small epsilon window).
    """
    threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    
    # Epsilon window around the threshold (using absolute value of threshold)
    epsilon = 0.05 * np.abs(threshold)
    if epsilon < 1e-4:
        epsilon = 0.005  # Avoid empty window if threshold is very close to zero
        
    condition = np.abs(portfolio_returns - threshold) <= epsilon
    
    # If the window is too small and no samples are found, widen it
    if not np.any(condition):
        epsilon = 0.20 * np.abs(threshold)
        if epsilon < 1e-3:
            epsilon = 0.02
        condition = np.abs(portfolio_returns - threshold) <= epsilon
        
    if not np.any(condition):
        # Fallback to nearest neighbors if still empty
        nearest_idx = np.argsort(np.abs(portfolio_returns - threshold))[:10]
        tail_asset_returns = asset_returns[nearest_idx]
    else:
        tail_asset_returns = asset_returns[condition]
        
    # MVaR is the negative expected return of the asset in this window
    mvar = -np.mean(tail_asset_returns, axis=0)
    return mvar

def calculate_component_var(mvar, weights):
    """
    Component VaR (CVaR) contribution of each asset.
    Sum of Component VaR equals total VaR.
    """
    return weights * mvar
