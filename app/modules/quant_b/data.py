import yfinance as yf
import pandas as pd

def load_assets(tickers,start_date,interval="1d"):
    if hasattr(start_date,'strftime'):
        start_str=start_date.strftime('%Y-%m-%d')
    else:
        start_str=str(start_date)

    data=yf.download(tickers,start=start_str,interval=interval,group_by='ticker',auto_adjust=True)
    
    df=pd.DataFrame()
    for t in tickers:
        try:
            if isinstance(data.columns,pd.MultiIndex):
                if t in data.columns:
                    df[t]=data[t]['Close']
            else:
                if 'Close' in data.columns:
                    df[t]=data['Close']
        except KeyError:
            continue
            
    df=df.ffill().bfill()
    return df