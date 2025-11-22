import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import numpy as np

from src.data_fetch import fetch_prices
from src.metrics import (
    simple_returns, portfolio_returns, cumulative_returns,
    rolling_vol, max_drawdown, historical_var, historical_cvar, parametric_var
)

from tabs.portfolio_dashboard import show_portfolio_dashboard
from tabs.spx_comparison import show_spx_comparison
from tabs.simulation_station import show_simulation_station

# --------------------------
# Helper Functions
# --------------------------
def metric_with_divider(col, label, value, border=True):
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

def st_alert(message, alert_type="info"):
    """
    Show a warning/info/success message and scroll to top reliably.
    """
    alert_func = {"info": st.info, "warning": st.warning, "success": st.success}.get(alert_type, st.info)
    alert_func(message)  # Render the alert

    # Scroll to top AFTER the alert exists
    st.markdown(
        """
        <script>
        setTimeout(function() {
            const el = document.querySelector('div[data-testid="stAlert"]');
            if(el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        }, 200);
        </script>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# Page Configs
# --------------------------
st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📊",
    layout='wide'
)

# For initiating scroll on top
message_placeholder = st.empty()

# --------------------------
# Load SPX Data
# --------------------------
@st.cache_data
def load_data():
    prices = fetch_prices(['^GSPC'])
    prices = prices.dropna()
    return prices

spx_prices = load_data()

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("Portfolio Settings")
initial_investment = st.sidebar.number_input("Initial Investment ($)", min_value=0, value=10000, step=1000)

# Add tickers
tickers = st.sidebar.container()
with tickers:
    tickers = st_tags(
        label="Add Assets",
        text="Press enter to add more",
        value=['AAPL', 'GOOG'],
        suggestions=["AAPL", "GOOG", "TSLA"]
    )
tickers = list(map(str.upper, tickers))

# Fetch prices for selected tickers
if tickers:
    prices = fetch_prices(tickers).dropna()
    close = prices['Close']

# Set portfolio weights
weights = []
if tickers:
    st.sidebar.subheader("Portfolio Weights (%)")
    for t in tickers:
        w = st.sidebar.slider(f'{t} Weight', min_value=0, max_value=100, value=100//len(tickers), step=1)
        weights.append(w)

total_weight = sum(weights)
st.sidebar.markdown(
    f"Total Weight Used: <span style='color:{'lightgreen' if total_weight==100 else 'red'}'>{total_weight}</span>/100",
    unsafe_allow_html=True
)

confidence_level = st.sidebar.selectbox("VaR Confidence Level", [0.90, 0.95, 0.99], index=1)

st.header('Portfolio Dashboard')

if total_weight != 100:
    st_alert("⚠️ Please set weights to total 100%.","info")
    st.stop()
else:
    st_alert("Dashboard updated!","success")
    
    # Custom time period selection
    st.subheader("Year Range")
    close.index = pd.to_datetime(close.index)
    years = sorted(close.index.year.unique())
    start_year, end_year = st.select_slider(
        "Select analysis period",
        options=years,
        value=(years[0],years[-1])
    )
    # Portfolio Year Filter
    close = close[(close.index.year >= start_year) & (close.index.year <= end_year)]

    # --------------------------
    # Calculations
    # --------------------------
    close.index = pd.to_datetime(close.index)
    returns = simple_returns(close[tickers])
    port_ret = portfolio_returns(returns, weights)
    cum_ret = cumulative_returns(port_ret)
    port_value = initial_investment * (cum_ret + 1)
    port_mean_ret = port_ret.mean()
    volatility_score = port_ret.std()
    trading_days = 252
    sharpe_ratio = (port_mean_ret * trading_days) / (volatility_score * np.sqrt(trading_days))
    window_size = 60
    roll_vol = rolling_vol(port_ret, window=window_size)
    drawdown_data = max_drawdown(port_ret)
    var = historical_var(port_ret, 1-confidence_level)
    cvar = historical_cvar(port_ret, 1-confidence_level)
    pvar = parametric_var(port_ret, 1-confidence_level)
    cash_var = initial_investment * var
    cash_cvar = initial_investment * cvar
    cash_pvar = initial_investment * pvar
    corr = returns.corr()

    st.session_state.last_results = {
        "returns": returns,
        "port_ret": port_ret,
        "cum_ret": cum_ret,
        "port_value": port_value,
        "port_mean_ret": port_mean_ret,
        "volatility_score": volatility_score,
        "sharpe_ratio": sharpe_ratio,
        "window_size": window_size,
        "roll_vol": roll_vol,
        "drawdown_data": drawdown_data,
        "var": var,
        "cvar": cvar,
        "pvar": pvar,
        "cash_var": cash_var,
        "cash_cvar": cash_cvar,
        "cash_pvar": cash_pvar,
        "corr": corr,
    }

# --------------------------
# Tabs
# --------------------------
if "last_results" not in st.session_state:
    st_alert("👉 Please set weights to total 100% to see results.","info")
    st.stop()

results = st.session_state.last_results
tab1, tab2, tab3 = st.tabs([
    "Portfolio Dashboard", 
    "Comparison with SPX",
    "Simulation Station"
])

with tab1:
    show_portfolio_dashboard(tickers, weights, initial_investment, close, results, metric_with_divider)

with tab2:
    show_spx_comparison(results, spx_prices, tickers, close, confidence_level, metric_with_divider)

with tab3:
    show_simulation_station(results['returns'],metric_with_divider)
