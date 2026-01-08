# app/modules/quant_a/strategies.py
import pandas as pd

def get_close(df, ticker):
    if isinstance(df.columns, pd.MultiIndex):
        # df[('Close','AAPL')]
        if ('Close', ticker) in df.columns:
            close = df[('Close', ticker)]
        else:
            # parfois l’ordre est inversé
            close = df[(ticker, 'Close')]
    else:
        close = df['Close']
    return close


def buy_and_hold(df, ticker):
    if isinstance(df.columns, pd.MultiIndex):
        close = df[ticker]['Close']
    else:
        close = df['Close']

    returns = close.pct_change().fillna(0)
    equity = (1 + returns).cumprod()
    return equity

# app/modules/quant_a/strategies.py
import pandas as pd

def momentum(df, ticker, lookback=10):
    close = get_close(df, ticker)

    ma = close.rolling(lookback).mean()
    signal = (close > ma).astype(int)  # 1 = invest, 0 = cash

    returns = close.pct_change().fillna(0) * signal.shift(1).fillna(0)
    equity = (1 + returns).cumprod()
    equity = equity / equity.iloc[0]  # Normalisation à 1 pour bien voir la ligne
    return equity


