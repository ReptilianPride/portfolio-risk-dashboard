import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_portfolio_dashboard(tickers, weights, initial_investment, close, results, metric_with_divider):
    returns = results['returns']
    port_ret = results["port_ret"]
    cum_ret = results["cum_ret"]
    port_value = results["port_value"]
    port_mean_ret = results["port_mean_ret"]
    volatility_score = results["volatility_score"]
    sharpe_ratio = results["sharpe_ratio"]
    window_size = results["window_size"]
    roll_vol = results["roll_vol"]
    drawdown_data = results["drawdown_data"]
    var = results["var"]
    cvar = results["cvar"]
    pvar = results["pvar"]
    cash_var = results["cash_var"]
    cash_cvar = results["cash_cvar"]
    cash_pvar = results["cash_pvar"]
    corr = results["corr"]

    # Portfolio table
    df = pd.DataFrame({
        "Ticker": tickers,
        "Weight": [f"{w}%" for w in weights] 
    })
    st.write("**Selected Tickers (w/ weights):**")
    st.dataframe(df)

    # Risk Metrics
    col1, col2, col3, col4 = st.columns(4)
    metric_with_divider(col1, "Mean Return", f"{port_mean_ret:.2%}")
    metric_with_divider(col1, "", "$"+str(round((initial_investment * port_mean_ret), 2)))
    metric_with_divider(col2, "Volatility (Std Dev)", f"{volatility_score:.2%}")
    metric_with_divider(col2, "", "$"+str(round((initial_investment * volatility_score), 2)))
    metric_with_divider(col3, "Sharpe Ratio (annualized)", f"{sharpe_ratio:.2f}")
    metric_with_divider(col3, "", "N/A")
    metric_with_divider(col4, "Max Drawdown", f"{-drawdown_data.min():.2%}")
    metric_with_divider(col4, "", "$"+str(round(-(initial_investment * drawdown_data.min()), 2)))

    st.markdown("---")

    # VaR metrics
    st.write(f"**Confidence Level (Daily)**: {var:.2%}")
    col1, col2, col3 = st.columns(3)
    metric_with_divider(col1, "Value at Risk (VaR)", f"{var:.2%}")
    metric_with_divider(col2, "Conditional VaR", f"{cvar:.2%}")
    metric_with_divider(col3, "Parametric VaR", f"{pvar:.2%}")

    col1, col2, col3 = st.columns(3)
    metric_with_divider(col1, "", "$"+str(round(cash_var, 2)))
    metric_with_divider(col2, "", "$"+str(round(cash_cvar, 2)))
    metric_with_divider(col3, "", "$"+str(round(cash_pvar, 2)))

    # Charts
    # Portfolio returns chart
    fig = px.line(port_value, title="Portfolio Returns")
    fig.update_xaxes(nticks=20)
    fig.update_traces(
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:,~s}<extra></extra>'
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title='Timeline',
        yaxis_title='Returns'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 2nd Row charts (x2)
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

    # 3rd row charts(x2)
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
        # To create shaded region
        fig.add_traces(go.Scatter(
            x=drawdown_data.index, 
            y=drawdown_data.values.flatten(), 
            fill='tozeroy',   # fill area to y=0
            mode='none',      # no line, just fill
            fillcolor='rgba(255,0,0,0.2)',  # red shading with transparency
            name='Shaded Area'
        ))
        fig.update_traces(line=dict(color="red"), selector=dict(type="scatter"))
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