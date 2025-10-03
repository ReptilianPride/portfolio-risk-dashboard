import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from src.metrics import (
    simple_returns, portfolio_returns, cumulative_returns,
    rolling_vol, max_drawdown, historical_var, historical_cvar,
    parametric_var
)


# helper functions
# To create the metric blocks with boundries and custom styles
def metric_with_divider(col, label, value, border=True):
    """Custom metric with optional vertical divider line."""
    border_style = "border-right:1px solid lightgray;" if border else ""
    with col:
        st.markdown(
            f"""
            <div style="{border_style} padding:10px; text-align:center;">
                <div style="font-size:1.1rem; font-weight:600; color:gray;">{label}</div>
                <div style="font-size:1.5rem; font-weight:700;">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# helper functions end

# --------------------------
# Page Configs
# --------------------------
st.set_page_config(
    page_title="Development",  # this sets the <title>
    page_icon="🚀",              # optional, sets the favicon
    layout='wide'
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
    default=close.columns[:-3]
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
            value=100//len(tickers),
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

valid_weights=total_weight==100
if not valid_weights:
    st.warning("⚠️ Warning: Total weight does not add up to 100%.")

# Main side
if valid_weights:
    st.success('Dashboard updated!')

    st.title('Stock Portfolio Risk Dashboard')
    st.markdown("A prototype dashboard showcasing risk analytics for selected assets.")

    st.subheader('Portfolio Overview')

    # Custom time period selection
    st.subheader("Date Range")
    close.index = pd.to_datetime(close.index)
    years = sorted(close.index.year.unique())
    start_year, end_year = st.select_slider(
        "Select analysis period",
        options=years,
        value=(years[0],years[-1])
    )
    close = close[(close.index.year >= start_year) & (close.index.year <= end_year)] # To filter as per selected timeframe

    # Calculation section
    returns=simple_returns(close[tickers])
    port_ret=portfolio_returns(returns,weights)
    cum_ret=cumulative_returns(port_ret)

    port_value=initial_investment*(cum_ret+1)
    
    port_mean_ret=port_ret.mean()
    volatility_score=port_ret.std()
    sharpe_ratio=port_mean_ret/volatility_score # sharpe ratio, need to check this out in more detail

    window_size=60 # Could be a user input
    roll_vol=rolling_vol(port_ret,window=window_size)

    drawdown_data=max_drawdown(port_ret)

    var=historical_var(port_ret,1-confidence_level)
    cvar=historical_cvar(port_ret,1-confidence_level)
    pvar=parametric_var(port_ret,1-confidence_level)

    cash_var = initial_investment * var
    cash_cvar = initial_investment * cvar
    cash_pvar = initial_investment * pvar

    corr=returns.corr()

    # Save into session_state
    st.session_state.last_results = {
        "returns": returns,
        "port_ret": port_ret,
        "cum_ret": cum_ret,
        "port_value":port_value,
        "port_mean_ret": port_mean_ret,
        "volatility_score": volatility_score,
        "sharpe_ratio": sharpe_ratio,
        "window_size":window_size,
        "roll_vol": roll_vol,
        "drawdown_data": drawdown_data,
        "var": var,
        "cvar": cvar,
        "pvar":pvar,
        "cash_var":cash_var,
        "cash_cvar":cash_cvar,
        "cash_pvar":cash_pvar,
        "corr": corr,
    }

# --------------------------
# Dashboard Layout
# --------------------------

# --------------------------
# Use last valid results (if available)
# --------------------------
if "last_results" not in st.session_state:
    st.info("👉 Please set weights to total 100% to see results.")
    st.stop()

results = st.session_state.last_results

# unpack variables
returns = results["returns"]
port_ret = results["port_ret"]
cum_ret = results["cum_ret"]
port_value=results['port_value']
port_mean_ret = results["port_mean_ret"]
volatility_score = results["volatility_score"]
sharpe_ratio = results["sharpe_ratio"]
window_size=results['window_size']
roll_vol = results["roll_vol"]
drawdown_data = results["drawdown_data"]
var = results["var"]
cvar = results["cvar"]
pvar=results['pvar']
cash_var=results['cash_var']
cash_cvar=results['cash_cvar']
cash_pvar=results['cash_pvar']
corr = results["corr"]

# Non chart based display for dashboard
df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": [f"{w}%" for w in weights] 
})
st.write("**Selected Tickers (w/ weights):**")
# st.write(f'**Portfolio startpoint:** {close.index.min().year}')
st.dataframe(df)

st.subheader('Risk Metrics')

# --- Risk Metrics ---
col1, col2, col3, col4 = st.columns(4)
metric_with_divider(col1, "Mean Daily Return", f"{port_mean_ret:.2%}")
metric_with_divider(col1, "", "$"+str(round((initial_investment * port_mean_ret), 2)))

metric_with_divider(col2, "Volatility (Std Dev)", f"{volatility_score:.2%}")
metric_with_divider(col2, "", "$"+str(round((initial_investment * volatility_score), 2)))

metric_with_divider(col3, "Sharpe Ratio", f"{sharpe_ratio:.2%}")
metric_with_divider(col3, "", "$"+str(round((initial_investment * sharpe_ratio), 2)))

metric_with_divider(col4, "Max Drawdown", f"{-drawdown_data.min():.2%}")
metric_with_divider(col4, "", "$"+str(round(-(initial_investment * drawdown_data.min()), 2)))

st.markdown("---")

# --- Confidence Level & VaR Metrics ---
st.write(f"**Confidence Level (Daily)**: {confidence_level:.2%}")
col1, col2, col3 = st.columns(3)
metric_with_divider(col1, "Value at Risk (VaR)", f"{var:.2%}")
metric_with_divider(col2, "Conditional VaR", f"{cvar:.2%}")
metric_with_divider(col3, "Parametric VaR", f"{pvar:.2%}")

col1, col2, col3 = st.columns(3)
metric_with_divider(col1, "", "$"+str(round(cash_var, 2)))
metric_with_divider(col2, "", "$"+str(round(cash_cvar, 2)))
metric_with_divider(col3, "", "$"+str(round(cash_pvar, 2)))


# --------------------------
# Dashboard Layout
# --------------------------
st.subheader('Charts')

# To show the portfolio returns chart
fig=px.line(port_value,title='Portfolio Returns')
fig.update_xaxes(nticks=20)
fig.update_traces(
    hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:,.2f}<extra></extra>'
)
fig.update_layout(
    showlegend=False,
    xaxis_title='Time',
    yaxis_title='Returns'
)
st.plotly_chart(fig,use_container_width=True)

col1,col2=st.columns(2)

with col1:
    # Return distribution
    fig=px.histogram(port_ret,nbins=50,title='Portfolio Return Distribution')
    fig.add_vline(x=-var, line_dash="dash", line_color='red', annotation_text=f"VaR ({-var:.2%})", annotation_position='top right')
    fig.add_vline(x=-cvar, line_dash="dot", line_color='white', annotation_text=f"CVaR ({-cvar:.2%})", annotation_position='top left')
    fig.update_layout(
        showlegend=False,
        xaxis_title='Daily Returns',
        yaxis_title='Frequency'
    )
    st.plotly_chart(fig,use_container_width=True)

    # Annualized Rolling Volatility
    fig=px.line(roll_vol,title=f"{window_size}-day Annualized Rolling Volitility")
    fig.update_xaxes(nticks=20)
    fig.update_traces(line=dict(color='orange'))
    fig.update_layout(
        showlegend=False,
        xaxis_title='Time',
        yaxis_title='Volatility'
    )
    st.plotly_chart(fig,use_container_width=True)


with col2:
    # Cumulative Returns Distribution
    fig = px.line(cum_ret, title="Cumulative Portfolio Returns")
    fig.update_xaxes(nticks=20)
    fig.update_layout(
        showlegend=False,
        xaxis_title='Daily Timeline',
        yaxis_title='Cumulative Returns'
    )
    st.plotly_chart(fig,use_container_width=True)

    # Max Drawdown
    fig=px.line(drawdown_data,title=f'Portfolio Drawdown (MaxDD:{drawdown_data.min():.3})')
    fig.update_xaxes(nticks=20)
    #   To create shaded region
    fig.add_traces(go.Scatter(
        x=drawdown_data.index, 
        y=drawdown_data.values.flatten(), 
        fill='tozeroy',   # fill area to y=0
        mode='none',      # no line, just fill
        fillcolor='rgba(255,0,0,0.2)',  # red shading with transparency
        name='Shaded Area'
    ))
    fig.update_traces(line=dict(color="red"), selector=dict(type="scatter"))
    #   To make the line color red
    fig.update_traces(line=dict(color="red"))
    fig.update_layout(
        showlegend=False,
        yaxis_title='Drawdown',
        xaxis_title='Time'
    )
    st.plotly_chart(fig,use_container_width=True)
    

# Asset Correlations
corr=returns[tickers].corr()
fig=px.imshow(corr,text_auto=True,aspect="auto",title="Asset Correlations",color_continuous_scale="RdYlBu")
st.plotly_chart(fig,use_container_width=True)

# To implement stress test