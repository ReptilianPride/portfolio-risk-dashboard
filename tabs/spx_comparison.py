import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.metrics import simple_returns, cumulative_returns, max_drawdown, historical_var, historical_cvar, parametric_var

def show_spx_comparison(results, spx_prices, tickers, close, confidence_level, metric_with_divider):
    port_ret = results["port_ret"]
    cum_ret = results["cum_ret"]
    trading_days = 252
    port_mean_ret = results["port_mean_ret"]
    volatility_score = results["volatility_score"]
    sharpe_ratio = results["sharpe_ratio"]
    drawdown_data = results["drawdown_data"]
    var = results["var"]
    cvar = results["cvar"]
    pvar = results["pvar"]

    st.subheader("Portfolio vs S&P 500 Comparison")

    spx_close = spx_prices['Close'].dropna()
    spx_close=spx_close.squeeze()
    spx_returns = simple_returns(spx_close)
    spx_cum_ret = cumulative_returns(spx_returns)
    spx_mean_ret = spx_returns.mean()
    spx_volatility_score = spx_returns.std()
    spx_sharpe_ratio = (spx_mean_ret * trading_days) / (spx_volatility_score * np.sqrt(trading_days))
    spx_max_drawdown = max_drawdown(spx_returns).min()
    spx_var = historical_var(spx_returns, 1-confidence_level)
    spx_cvar = historical_cvar(spx_returns, 1-confidence_level)
    spx_pvar = parametric_var(spx_returns, 1-confidence_level)

    # Metrics comparisons
    # --- Risk Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    metric_with_divider(col1, "Mean Daily Return", f"{port_mean_ret:.2%}")
    metric_with_divider(col1, "S&P", f"{spx_mean_ret:.2%}")

    metric_with_divider(col2, "Daily Volatility (Std Dev)", f"{volatility_score:.2%}")
    metric_with_divider(col2, "S&P", f"{spx_volatility_score:.2%}")

    metric_with_divider(col3, "Sharpe Ratio (Annualized)", f"{sharpe_ratio:.2f}")
    metric_with_divider(col3, "S&P", f"{spx_sharpe_ratio:.2f}")

    metric_with_divider(col4, "Daily Max Drawdown", f"{-drawdown_data.min():.2%}")
    metric_with_divider(col4, "S&P", f"{-spx_max_drawdown:.2%}")

    st.markdown("---")

    # --- Confidence Level & VaR Metrics ---
    st.write(f"**Confidence Level (Daily)**: {confidence_level:.2%}")
    col1, col2, col3 = st.columns(3)
    metric_with_divider(col1, "Daily Value at Risk (VaR)", f"{var:.2%}")
    metric_with_divider(col2, "Daily Conditional VaR", f"{cvar:.2%}")
    metric_with_divider(col3, "Daily Parametric VaR", f"{pvar:.2%}")

    col1, col2, col3 = st.columns(3)
    metric_with_divider(col1, "S&P", f"{spx_var:.2%}")
    metric_with_divider(col2, "S&P", f"{spx_cvar:.2%}")
    metric_with_divider(col3, "S&P", f"{spx_pvar:.2%}")

    # Charting
    st.subheader('Charts')
    compare_df = pd.concat([cum_ret.rename("Portfolio"), spx_cum_ret.squeeze().rename("SPX")], axis=1).fillna(0)
    compare_df = ((compare_df + 1) / (compare_df.iloc[0] + 1)) * 100

    # Classical Returns plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=compare_df.index, y=compare_df["Portfolio"], mode="lines", name="Portfolio",line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=compare_df.index, y=compare_df["SPX"], mode="lines", name="S&P 500", line=dict(dash="dash")))
    st.plotly_chart(fig, use_container_width=True)


    # Differenced Area Plot
    compare_df['differenced']=compare_df[compare_df.columns[0]]-compare_df[compare_df.columns[1]]
    fig = go.Figure()
    # --- Green area for positive values ---
    fig.add_trace(go.Scatter(
        x=compare_df.index,
        y=np.where(compare_df['differenced'] > 0, compare_df['differenced'], 0),
        fill='tozeroy',
        mode='none',
        fillcolor='rgba(0, 200, 0, 0.5)',  # semi-transparent green
        name='Outperformance'
    ))
    fig.add_trace(go.Scatter(
        x=compare_df.index,
        y=np.where(compare_df['differenced'] < 0, compare_df['differenced'], 0),
        fill='tozeroy',
        mode='none',
        fillcolor='rgba(255, 16, 0, 0.5)',  # reddish orange
        name='Underperformance'
    ))
    fig.update_layout(
        title="Portfolio vs SPX — Differenced Area Plot",
        xaxis_title="Date",
        yaxis_title="Portfolio - SPX (Difference)",
        template="plotly_white",
        hovermode='x unified',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)