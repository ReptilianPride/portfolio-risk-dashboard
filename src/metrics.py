# Location: src/metrics.py

import numpy as np
import pandas as pd
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