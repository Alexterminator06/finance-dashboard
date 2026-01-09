import pandas as pd
import numpy as np

def calculate_portfolio(df,weights=None):

    if weights is None:
        n_assets=len(df.columns)
        weights=[1/n_assets]*n_assets
    else:
        total=sum(weights)
        if total>0:
            weights=[w/total for w in weights]
        else:
            n_assets=len(df.columns)
            weights=[1/n_assets]*n_assets
    
    returns=df.pct_change().dropna()
    port_returns=returns.dot(weights)
    portfolio_value=(1 + port_returns).cumprod()
    
    if not portfolio_value.empty:
        portfolio_value=portfolio_value/portfolio_value.iloc[0]
        
    return portfolio_value