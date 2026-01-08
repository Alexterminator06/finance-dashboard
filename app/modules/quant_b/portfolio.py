import pandas as pd

def equal_weight_portfolio(df):
    weights = [1/len(df.columns)] * len(df.columns)
    returns = df.pct_change().dropna()
    port_returns = returns.dot(weights)
    return (1 + port_returns).cumprod()
