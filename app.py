# app.py
import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
from src.data_fetch import fetch_prices
from src.metrics import (
    simple_returns, portfolio_returns, rolling_vol,
    max_drawdown, historical_var, historical_cvar
)
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Portfolio Risk Dashboard — Prototype")

# Sidebar for inputs
with st.sidebar:
    tickers = st.text_input("Tickers (comma-separated)", "AAPL,MSFT,GOOGL,AMZN,TSLA,SPY,TLT")
    # tickers = st_tags(
    #     label='Tickers',
    #     text='Press enter to add more',
    #     value=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "TLT"],
    #     suggestions=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "TLT"],
    #     maxtags=20,
    # )
    start = st.date_input("Start", value=pd.to_datetime("2011-01-01"))
    end = st.date_input("End", value=pd.to_datetime("today"))
    weights_text = st.text_input("Weights (comma)", "0.15,0.15,0.15,0.15,0.1,0.2,0.1")
    load_btn = st.button("Load")

# Only compute and show results if user clicks "Load"
if load_btn:
    tick_list = [t.strip() for t in tickers.split(",")]
    # tick_list=tickers
    weights = [float(x) for x in weights_text.split(",")]
    prices = fetch_prices(tick_list, start, end)
    returns = simple_returns(prices)
    port_ret = portfolio_returns(returns, weights)

    # Show metrics in main page (not sidebar)
    st.metric("Hist VaR (95%)", f"{historical_var(port_ret, .05):.2%}")
    st.metric("Hist CVaR (95%)", f"{historical_cvar(port_ret, .05):.2%}")

    # Plot in main page
    st.plotly_chart(
        px.line((1 + port_ret).cumprod(), title="Portfolio cumulative"),
        use_container_width=True
    )
