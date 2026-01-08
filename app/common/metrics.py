import numpy as np

def sharpe_ratio(returns, freq=252):
    mean = returns.mean() * freq
    vol = returns.std() * np.sqrt(freq)
    return mean / vol if vol else 0

def max_drawdown(equity):
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return dd.min()
