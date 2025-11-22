import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.metrics import monte_carlo_optimize
from src.metrics import monte_carlo_optimize_wprogress
from src.metrics import exhaustive_optimize

def show_simulation_station(returns_df,metric_with_divider):


    st.subheader("Monte Carlo Portfolio Optimization")

    # Parameters for running monte carlo simulations
    number_of_simulations=st.number_input("Number of Simulations", min_value=0, step=1, value=5000)
    risk_free_rate=st.number_input("Risk free rate", min_value=0.0, max_value=0.07, step=0.01, value=0.0)

    if st.button("Run Monte Carlo Optimization"):
        
        # Progress bar setups
        progress_bar = st.progress(0)
        def progress_callback(progress):
            progress_bar.progress(progress)
        
        # Running simulations
        mc_best=monte_carlo_optimize_wprogress(returns_df, number_of_simulations, risk_free_rate,progress_callback=progress_callback)
        
        progress_bar.empty()
        
        # Results
        st.subheader("Simulation Output")
        col1, col2, col3 = st.columns(3)
        metric_with_divider(col1, "Optimal Sharpe", f"{mc_best['Optimal Sharpe'].iloc[0]:.2f}")
        metric_with_divider(col2, "Expected Annual Return", f"{mc_best['Exp Return (annual)'].iloc[0]:.2%}")
        metric_with_divider(col3, "Annual Volatility", f"{mc_best['Volatility (annual)'].iloc[0]:.2%}")

        st.subheader("Asset Weight Distribution")
        st.dataframe(mc_best[mc_best.columns[:2]])



