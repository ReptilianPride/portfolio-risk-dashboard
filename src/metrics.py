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
def cumulative_return(port_ret):
    return (1+port_ret).cumprod()-1

# Calculate rolling volitility ffrom portfolio returns
def rolling_vol(port_ret,window=30,annualize=True):
    vol=port_ret.rolling(window).std()
    if annualize:
        vol=vol*np.sqrt(252)
    return vol