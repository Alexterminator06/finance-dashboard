import numpy as np

def sharpe_ratio(returns,freq=252):
    mean=returns.mean()*freq
    vol=returns.std()*np.sqrt(freq)
    return mean/vol if vol else 0

def max_drawdown(equity):
    peak=equity.cummax()
    dd=(equity-peak)/peak
    return dd.min()

def calculate_correlation(df):
    returns=df.pct_change().dropna()
    return returns.corr()

def portfolio_volatility(portfolio_series):
    #(252 jours de trading)
    returns=portfolio_series.pct_change().dropna()
    return returns.std()*np.sqrt(252)