import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

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

# Extract only Close prices
close = prices['Close']

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("Portfolio Settings")

tickers = st.sidebar.multiselect(
    "Select Assets",
    options=close.columns,
    default=["AAPL", "AMZN", "MSFT"]
)

weights = []
if tickers:
    st.sidebar.subheader("Portfolio Weights")
    for t in tickers:
        w = st.sidebar.slider(f"{t} weight", 0.0, 1.0, 1.0/len(tickers), 0.01)
        weights.append(w)
    # Normalize weights
    weights = np.array(weights) / np.sum(weights)

confidence_level = st.sidebar.selectbox("VaR Confidence Level", [0.90, 0.95, 0.99], index=1)
initial_investment = st.sidebar.number_input("Initial Investment ($)", 10000, step=1000)

# --------------------------
# Portfolio Calculations
# --------------------------
returns = close.pct_change().dropna()
portfolio_returns = (returns[tickers] @ weights)

cum_returns = (1 + portfolio_returns).cumprod()

mean_return = portfolio_returns.mean()
volatility = portfolio_returns.std()
sharpe_ratio = mean_return / volatility

VaR = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
CVaR = portfolio_returns[portfolio_returns <= VaR].mean()

# --------------------------
# Dashboard Layout
# --------------------------
st.title("📊 Portfolio Risk Dashboard")
st.markdown("A prototype dashboard showcasing risk analytics for selected assets.")

st.subheader("Portfolio Overview")
st.write(f"**Selected Tickers:** {', '.join(tickers)}")
st.write(f"**Weights:** {np.round(weights, 2)}")

col1, col2, col3 = st.columns(3)
col1.metric("Mean Daily Return", f"{mean_return:.4f}")
col2.metric("Volatility (Std Dev)", f"{volatility:.4f}")
col3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

st.subheader("Risk Metrics")
st.write(f"**VaR ({int(confidence_level*100)}%):** {VaR:.4f}")
st.write(f"**CVaR:** {CVaR:.4f}")

# --------------------------
# Charts
# --------------------------
st.subheader("Cumulative Returns")
fig1 = px.line(cum_returns, title="Cumulative Portfolio Returns")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Return Distribution")
fig2 = px.histogram(portfolio_returns, nbins=50, title="Portfolio Return Distribution")
fig2.add_vline(x=VaR, line_color="red", annotation_text="VaR", annotation_position="top left")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Correlation Heatmap")
corr = returns[tickers].corr()
fig3 = px.imshow(corr, text_auto=True, aspect="auto", title="Asset Correlations")
st.plotly_chart(fig3, use_container_width=True)

# --------------------------
# Stress Test
# --------------------------
st.subheader("Stress Test")
shock = st.slider("Apply % shock to all assets", -0.5, 0.5, 0.0, 0.01)
st.write(f"If all assets drop by {shock*100:.1f}%, portfolio impact = {(shock * np.sum(weights)):.2%}")
