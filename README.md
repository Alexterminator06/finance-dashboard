Financial Dashboard & Portfolio Manager

Welcome to my Finance Dashboard. This application is designed to simulate trading strategies on single assets (Quant A) and analyze multi-asset portfolios (Quant B).

Key Features

Quant A: Single Asset Analysis
Focuses on specific stocks, crypto, or forex pairs.
Strategy Backtesting: Compare "Buy & Hold" against 4 active strategies:
    Momentum (Trend Following)
    Bollinger Bands (Mean Reversion)
    Dual SMA (Golden/Death Cross)
    RSI (Oscillator Strategy)
AI Prediction: A machine learning model (Linear Regression) that forecasts the next day's closing price with a visual confidence indicator.
Financial Metrics: Real-time calculation of Sharpe Ratio, Max Drawdown, Net Profit, and Daily Win Rate.
Interactive Charts: Plotly graphs combining price history, strategy signals, and AI projections.

Quant B: Portfolio Management
Simulates the performance of a diversified basket of assets.
Custom Allocation: Choose between Equal Weighting or define your own custom weights for each asset.
Date Selection: Test portfolio resilience over specific historical periods.
Risk Analysis: visual Correlation Matrix and Annualized Volatility metrics.
Performance Tracking: Compare the portfolio's growth against individual asset performance.

Automation (Cron Job)
Daily Reporting: Includes a `daily_report.py` script designed to run automatically via a Linux Cron job.
Archives: Generates and saves key market metrics to a local file every day at 20:00, ensuring you have a historical log of market states.

Installation & Setup
Follow these steps to get the dashboard running on your local machine.

1/ Clone the repository

git clone [https://github.com/your-username/finance-dashboard.git](https://github.com/your-username/finance-dashboard.git)
cd finance-dashboard

2/use (venv) for python

3/Enter this line in the terminal : python -m streamlit run app/streamlit_app.py