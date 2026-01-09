import yfinance as yf

def load_asset(ticker,period="6mo",interval="1h"):
    data=yf.download(ticker,period=period,interval=interval)
    return data
