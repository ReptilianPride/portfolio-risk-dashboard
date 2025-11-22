# Location: src/metrics.py

import numpy as np
import pandas as pd
from itertools import product
from scipy.stats import norm

# Calculate percentage change
def simple_returns(prices):
    return prices.pct_change().dropna()

# Calculate portfolio returns
def portfolio_returns(returns_df,weights):
    w=np.array(weights)
    w=w/w.sum()
    return returns_df.dot(w)

# Calculate the cumulative returns from portfolio returns
def cumulative_returns(port_ret):
    return (1+port_ret).cumprod()-1

# Calculate rolling volitility from portfolio returns
def rolling_vol(port_ret,window=30,annualize=True):
    vol=port_ret.rolling(window).std()
    if annualize:
        vol=vol*np.sqrt(252)
    return vol

# Calculate the max drawdown from the portfolio returns
# I think there is a need for using drawdown.min()
def max_drawdown(port_ret):
    cum=(1+port_ret).cumprod()
    running_max=cum.cummax()
    drawdown=(cum/running_max)-1
    return drawdown

# Calculate the Value at Risk from the portfolio returns
def historical_var(port_ret, alpha=0.05):
    q=np.quantile(port_ret,alpha)
    var=-q
    return var

# Calculate the Conditional Value at Risk
def historical_cvar(port_ret,alpha=0.05):
    q=np.quantile(port_ret,alpha)
    tail=port_ret[port_ret<=q]
    cvar=-tail.mean()
    return cvar

# Calculate the Parametric Value at Risk
def parametric_var(port_ret,alpha=0.05):
    mu=port_ret.mean()
    sigma=port_ret.std()
    z=norm.ppf(alpha)
    var=-(mu+sigma*z)
    return var


# Monte Carlo Function
def monte_carlo_optimize(returns_df,num_sim=5000, risk_free_rate=0.0):
    """
    Optimizing for maximum sharpe ratio
    """

    n_assets=returns_df.shape[1]
    results=[]

    mean_returns=returns_df.mean()
    cov_matrix=returns_df.cov()

    for _ in range(num_sim):
        # To find the weights that sum up to 1 as per the number of assets
        w=np.random.random(n_assets)
        w=w/w.sum()

        port_return=np.dot(w,mean_returns)*252 # Annualized
        port_vol=np.sqrt(w.T @ cov_matrix @ w)*np.sqrt(252) # Annualized

        sharpe=(port_return-risk_free_rate)/port_vol

        results.append([port_return,port_vol,sharpe,w])

    # Convert to dataframe
    results_df=pd.DataFrame(results,columns=["Return","Volatility","Sharpe","Weights"])

    # Pick best sharpe ratio
    best = results_df.loc[results_df['Sharpe'].idxmax()]

    # Making weights as whole numbers
    weights_percent = best['Weights'] * 100  # scale to 0-100
    floored = np.floor(weights_percent)      # take floor of each weight
    remainder = int(100 - floored.sum())     # how much we need to add to reach 100

    # Distribute remainder to the largest fractional parts
    indices = np.argsort(weights_percent - floored)[-remainder:]
    floored[indices] += 1

    final_weights = floored.astype(int)

    # Return the information
    best_weights = pd.DataFrame({
        "Ticker":returns_df.columns,
        "Optimal Weight Percent":final_weights
    })

    best_weights["Optimal Sharpe"] = best["Sharpe"]
    best_weights["Exp Return (annual)"] = best["Return"]
    best_weights["Volatility (annual)"] = best["Volatility"]

    return best_weights


# Monte carlo with progress bar addition(same as above)
def monte_carlo_optimize_wprogress(returns_df, num_sim=5000, risk_free_rate=0.0, progress_callback=None):
    """
    Optimizing for maximum sharpe ratio with optional progress callback.
    """

    n_assets = returns_df.shape[1]
    results = []

    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()

    for i in range(num_sim):
        w = np.random.random(n_assets)
        w = w / w.sum()

        port_return = np.dot(w, mean_returns) * 252
        port_vol = np.sqrt(w.T @ cov_matrix @ w) * np.sqrt(252)
        sharpe = (port_return - risk_free_rate) / port_vol

        results.append([port_return, port_vol, sharpe, w])

        # Update progress bar if callback is provided
        if progress_callback:
            if i % max(1, num_sim // 100) == 0:  # update ~100 times
                progress_callback(i / num_sim)

    # Final progress = 100%
    if progress_callback:
        progress_callback(1.0)

    # Convert to dataframe
    results_df = pd.DataFrame(results, columns=["Return", "Volatility", "Sharpe", "Weights"])
    best = results_df.loc[results_df["Sharpe"].idxmax()]

    weights_percent = best['Weights'] * 100
    floored = np.floor(weights_percent)
    remainder = int(100 - floored.sum())
    indices = np.argsort(weights_percent - floored)[-remainder:]
    floored[indices] += 1
    final_weights = floored.astype(int)

    best_weights = pd.DataFrame({
        "Ticker": returns_df.columns,
        "Optimal Weight Percent": final_weights
    })
    best_weights["Optimal Sharpe"] = best["Sharpe"]
    best_weights["Exp Return (annual)"] = best["Return"]
    best_weights["Volatility (annual)"] = best["Volatility"]

    return best_weights


# TOO INTENSIVE (DISABLED FOR NOW)
# Experimental exhaustive monte carlo
def exhaustive_optimize(returns_df, step=0.01, risk_free_rate=0.0):
    
    n_assets = returns_df.shape[1]

    if(n_assets>3):
        raise Exception("High Intensity Operation! (ABORTING)")

    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    
    # Generate all possible weight combinations
    weight_range = np.arange(0, 1 + step, step)
    all_combinations = [w for w in product(weight_range, repeat=n_assets) if np.isclose(sum(w), 1)]
    
    results = []
    
    for w in all_combinations:
        w = np.array(w)
        port_return = np.dot(w, mean_returns) * 252
        port_vol = np.sqrt(w.T @ cov_matrix @ w) * np.sqrt(252)
        sharpe = (port_return - risk_free_rate) / port_vol
        results.append([port_return, port_vol, sharpe, w])
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results, columns=["Return", "Volatility", "Sharpe", "Weights"])
    
    # Pick best Sharpe ratio
    best = results_df.loc[results_df['Sharpe'].idxmax()]
    
    # Convert weights to integers summing to 100
    weights_percent = best['Weights'] * 100
    floored = np.floor(weights_percent)
    remainder = int(100 - floored.sum())
    indices = np.argsort(weights_percent - floored)[-remainder:]
    floored[indices] += 1
    final_weights = floored.astype(int)
    
    # Return as DataFrame
    best_weights = pd.DataFrame({
        "Ticker": returns_df.columns,
        "Optimal Weight Percent": final_weights
    })
    best_weights["Optimal Sharpe"] = best["Sharpe"]
    best_weights["Exp Return (annual)"] = best["Return"]
    best_weights["Volatility (annual)"] = best["Volatility"]
    
    return best_weights
