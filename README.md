# Portfolio Risk Dashboard

The **Portfolio Risk Dashboard** is an interactive web-based tool built using **Streamlit**, enabling users to analyze and visualize portfolio risk metrics, volatility trends, and **Value-at-Risk (VaR)** estimates. Users can construct portfolios, allocate custom weights, and benchmark performance against the **S&P 500 (SPX)**. Additionally, the dashboard includes a **Monte Carlo simulation** feature that helps identify the **optimal portfolio weights** for a given number of simulations, allowing users to explore numerous portfolio combinations and determine allocations that maximize returns while managing risk.  


This project demonstrates the intersection of **data science** and **financial risk analytics**, providing value for quantitative analysts, risk modelers, and financial data scientists.  

![Monte Carlo Update](https://img.shields.io/badge/Anouncement-New_red)  
A **Monte Carlo simulation** has been added to identify the **optimal portfolio weights** for a given number of simulations. This enhancement allows users to explore numerous portfolio combinations and determine the weight allocation that maximizes returns while managing risk.



## Key Features

### Monte Carlo Simulation Station
Find out the best asset weightage for the best outcomes using Monte Carlo Simulations

### Dynamic Portfolio Output
Add custom tickers and define allocation weights interactively.  

### Risk Metrics:
- Mean Daily Returns
- Volatility
- Sharpe Ratio (annualized)
- Maximum Drawdown

### Value-at-Risk (VaR) Suite
- Historical VaR
- Conditional VaR
- Parametric VaR

### Comparison Analysis
Benchmark the portfolio with the S&P 500 (^GSPC) with normalized cumulative returns and difference area plots.

### Interactive Visuals
Providing a visual overview to understand the plots better.

### Custom Date Rage Filtering
Analyze using a specific historical time windows.

## Preview
### NEWEST ADDITION!. Simulation Station Tab
![Main Dashboard](assets/images/tab3.png)

### 1. Main Dashboard
![Main Dashboard](assets/images/tab1-1.png)

### 2. Charts in Dashboard
![Risk Metrics](assets/images/tab1-2.png)

### 3. S&P 500 Comparison Tab (Part 1)
![Main Charts](assets/images/tab2-1.png)

### 4. S&P 500 Comparison Tab (Part 2)
![Compare Charts](assets/images/tab2-2.png)

## Tech Stacks
| Layer                    | Tools / Libraries                                        |
| :----------------------- | :------------------------------------------------------- |
| **Frontend**             | Streamlit, Plotly                                        |
| **Backend / Analytics**  | Pandas, NumPy                                            |
| **Visualization**        | Matplotlib, Plotly Express, Plotly Graph Objects         |
| **Data Source**          | `yfinance` or other market data API via `fetch_prices()` |
| **Supporting Utilities** | Custom modules (`src.data_fetch`, `src.metrics`)         |


## Project Structure
```bash
portfolio-risk-dashboard/
│
├── src/
│   ├── data_fetch.py          # Data loading and cleaning
│   ├── metrics.py             # Financial & risk computation functions
│
├── tabs/
│   ├── portfolio_dashboard.py          # Portfolio Tab Dashboard
│   ├── spx_comparison.py               # SPX Comparison Dashboard
│   ├── simulation_station.py           # Simulation Station Dashboard
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── assets/                    # Content for README placeholders
```

## 🧠 Features
- Portfolio optimization and performance measurement
- Risk assessment through VaR / CVaR / drawdown analysis
- Sharpe ratio & volatility tracking
- Rolling window volatility estimation
- Time-series data manipulation using pandas MultiIndex
- Comparative benchmarking against market indices
- Monte Carlo Simulation for portfolio optimization

## Included Charts
- 📈 Portfolio Cumulative Returns
- 📉 Drawdown Curve
- 📊 Return Distribution with VaR & CVaR markers
- 🧩 Asset Correlation Heatmap
- 🔄 Rolling Volatility Chart
- ⚖️ Portfolio vs S&P Performance Overlay

# Instructions: How to run
## 1. Close this repository
```bash
git clone https://github.com/alanraju/portfolio-risk-dashboard.git
cd portfolio-risk-dashboard
```

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Run the dashboard
```bash
streamlit run app.py
```

# Future Enhancements
- ✅ Portfolio optimization using Mean-Variance (Markowitz) model
- ✅ Incorporate Sharpe, Sortino, and Calmar ratios dynamically
- ✅ Add sector & asset-class diversification charts
- ✅ Better portfolio comparison logic

*With luv from a Risk Enthusiast <3*
