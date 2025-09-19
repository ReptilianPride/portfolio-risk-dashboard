# Location: src/data_fetch.py

import yfinance as yf
import pandas as pd

def fetch_prices(tickers,start=None,end=None):
    """
    EXAMPLE USE:
    
    For given start and end dates:
        fetch_prices(tickers, start="1980-01-01", end="2025-01-01")

    ===OR===

    For maximum available dates:
        fetch_prices(tickers)
    """
    tickers=[t.strip().upper() for t in tickers]
    if start and end:
        data=yf.download(tickers,start=start,end=end,auto_adjust=True)['Close']
    else:
        data=yf.download(tickers,period='max',auto_adjust=True)
    
    # If single ticker, resulting data is series, converting to dataframe
    if isinstance(data,pd.Series):
        data=data.to_frame()
    return data
