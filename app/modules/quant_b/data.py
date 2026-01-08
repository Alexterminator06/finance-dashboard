import yfinance as yf

def load_assets(tickers, period="6mo", interval="1h"):
    df = yf.download(tickers, period=period, interval=interval)["Close"]
    df = df.ffill().bfill()
    return df
