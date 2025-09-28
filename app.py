import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from src.metrics import (
    simple_returns, portfolio_returns, cumulative_returns,
    rolling_vol, max_drawdown, historical_var, historical_cvar
)

# --------------------------
# Page Configs
# --------------------------
st.set_page_config(
    page_title="Development",  # this sets the <title>
    page_icon="🚀",              # optional, sets the favicon
)

# --------------------------
# Load Data
# --------------------------
@st.cache_data
def load_data():
    # Replace this with your own loading step
    prices = pd.read_csv("assets/data/prices.csv",header=[0,1],index_col=0,parse_dates=True)
    prices=prices.dropna()
    return prices

prices = load_data()
close=prices['Close']

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("Portfolio Settings")

# Get the initial investment
initial_investment = st.sidebar.number_input("Initial Investment ($)", 10000, step=1000)

# Text tag area to add assets
tickers=st.sidebar.multiselect(
    "Add Assets",
    # options=[], # Keep this one
    options=close.columns, # REMOVE: Just for now
    default=['AAPL','MSFT']
)

# To set the weights
weights=[]
if tickers:
    st.sidebar.subheader("Portfolio Weights (%)")
    for t in tickers:
        w=st.sidebar.slider(
            f'{t} Weight',
            min_value=0,
            max_value=100,
            value=50,
            step=1 # Uses only int for now
        )
        weights.append(w)

total_weight=sum(weights)

st.sidebar.markdown(
    f"Total Weight Used: <span style='color:{'lightgreen' if total_weight==100 else 'red'}'>{total_weight}</span>/100",
    unsafe_allow_html=True
)

# To get the confident level for VaR calculations
confidence_level = st.sidebar.selectbox("VaR Confidence Level", [0.90, 0.95, 0.99], index=1)

# Main side
if(total_weight!=100):
    st.warning("⚠️ Warning: Total weight does not add up to 100%.")
else:
    # Calculation section
    returns=simple_returns(close[tickers])
    port_ret=portfolio_returns(returns,weights)
    cum_ret=cumulative_returns(port_ret)
    
    port_mean_ret=port_ret.mean()
    volatility_score=port_ret.std()
    sharpe_ratio=port_mean_ret/volatility_score # sharpe ratio, need to check this out in more detail

    window_size=60 # Could be a user input
    roll_vol=rolling_vol(port_ret,window=window_size)

    drawdown_data=max_drawdown(port_ret)

    var=historical_var(port_ret,1-confidence_level)
    cvar=historical_cvar(port_ret,1-confidence_level)

    corr=returns.corr()

    # --------------------------
    # Dashboard Layout
    # --------------------------

    st.title('Stock Portfolio Risk Dashboard')
    st.markdown("A prototype dashboard showcasing risk analytics for selected assets.")

    st.subheader('Portfolio Overview')

    df = pd.DataFrame({
        "Ticker": tickers,
        "Weight": [f"{w}%" for w in weights] 
    })
    st.write("**Selected Tickers (w/ weights):**")
    st.write(f'**Portfolio startpoint:** {close.index.min().year}')
    st.dataframe(df)

    st.subheader('Risk Metrics')

    col1,col2,col3=st.columns(3)
    col1.metric("**Mean Daily Return**", f"{port_mean_ret:.4f}")
    col2.metric("**Volatility (Std Dev)**", f"{volatility_score:.4f}")
    col3.metric("**Sharpe Ratio**", f"{sharpe_ratio:.2f}")

    st.write(f"**Confidence Level: {confidence_level:.2%}**")

    col1,col2=st.columns(2)
    col1.metric('**Value at Risk (VaR)**',round(var,3))
    col2.metric('**Conditional VaR**',round(cvar,3))

    # --------------------------
    # Dashboard Layout
    # --------------------------
    st.subheader('Charts')

    # Return distribution
    fig1=px.histogram(port_ret,nbins=50,title='Portfolio Return Distribution')
    fig1.add_vline(x=-var, line_dash="dash", line_color='red', annotation_text=f"VaR ({-var:.2%})", annotation_position='top right')
    fig1.add_vline(x=-cvar, line_dash="dot", line_color='white', annotation_text=f"CVaR ({-cvar:.2%})", annotation_position='top left')
    fig1.update_layout(
        showlegend=False,
        xaxis_title='Daily Returns',
        yaxis_title='Count'
    )
    st.plotly_chart(fig1,use_container_width=True)

    # Cumulative Returns Distribution
    fig2 = px.line(cum_ret, title="Cumulative Portfolio Returns")
    fig2.update_xaxes(nticks=20)
    fig2.update_layout(
        showlegend=False,
        xaxis_title='Daily Timeline',
        yaxis_title='Cumulative Returns'
    )
    st.plotly_chart(fig2,use_container_width=True)

    # Max Drawdown
    fig3=px.line(drawdown_data,title='Portfolio Drawdown')
    st.plotly_chart(fig3,use_container_width=True)
    # edit code here currently


    # Asset Correlations
    corr=returns[tickers].corr()
    fig4=px.imshow(corr,text_auto=True,aspect="auto",title="Asset Correlations")
    st.plotly_chart(fig4,use_container_width=True)