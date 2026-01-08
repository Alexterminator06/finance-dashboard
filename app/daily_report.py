import yfinance as yf
import pandas as pd
from datetime import datetime
import os

TICKERS = ["AAPL", "BTC-USD", "EURUSD=X"]
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

def calculate_metrics(df, ticker):
    if isinstance(df.columns, pd.MultiIndex):
        close = df[ticker]['Close']
    else:
        close = df['Close']

    volatility = close.pct_change().std() * (252**0.5)
    max_drawdown = (close / close.cummax() - 1).min()
    open_price = close.iloc[0]
    close_price = close.iloc[-1]

    return {
        "Ticker": ticker,
        "Open": open_price,
        "Close": close_price,
        "Volatility": volatility,
        "Max Drawdown": max_drawdown
    }

def generate_daily_report(tickers=TICKERS):
    report = []
    for ticker in tickers:
        df = yf.download(ticker, period="6mo", interval="1d", group_by='ticker', auto_adjust=True)
        metrics = calculate_metrics(df, ticker)
        report.append(metrics)
    
    report_df = pd.DataFrame(report)
    
    # Sauvegarde CSV
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(REPORT_FOLDER, f"daily_report_{today}.csv")
    report_df.to_csv(filename, index=False)
    
    return report_df