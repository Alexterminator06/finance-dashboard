import pandas as pd

def get_close(df,ticker):
    if isinstance(df.columns,pd.MultiIndex) and ticker in df.columns:
        return df[ticker]['Close']

    elif 'Close' in df.columns:
        return df['Close']

    elif isinstance(df.columns,pd.MultiIndex) and 'Close' in df.columns:
        return df['Close'][ticker]
        
    else:
        raise KeyError(f"Impossible de trouver le prix de clôture pour {ticker} dans les données.")

def buy_and_hold(df,ticker):
    close=get_close(df,ticker)
    returns=close.pct_change().fillna(0)
    equity=(1+returns).cumprod()
    return equity

def momentum(df,ticker,lookback=10):
    close=get_close(df,ticker)
    ma=close.rolling(lookback).mean()
    signal=(close>ma).astype(int)    
    returns=close.pct_change().fillna(0)
    strategy_returns=returns*signal.shift(1).fillna(0)
    equity=(1+strategy_returns).cumprod()
    
    if not equity.empty:
        equity=equity/equity.iloc[0]
        
    return equity

def bollinger_bands_strategy(df,ticker,window=20,num_std=2):
    close=get_close(df,ticker)
    ma=close.rolling(window=window).mean()
    std=close.rolling(window=window).std()
    upper_band=ma+(std*num_std)
    lower_band=ma-(std*num_std)
    
    signal=pd.Series(0,index=close.index)
    position=0
    signal_values=[]
    for i in range(len(close)):
        price=close.iloc[i]
        lb=lower_band.iloc[i]
        ub=upper_band.iloc[i]
        
        if price<lb:
            position=1 #Achat
        elif price>ub:
            position=0 #Vente
        
        signal_values.append(position)       
    signal=pd.Series(signal_values,index=close.index)
    returns=close.pct_change().fillna(0)*signal.shift(1).fillna(0)
    equity=(1+returns).cumprod()
    
    if not equity.empty: equity=equity/equity.iloc[0]
    return equity

def dual_sma_crossover(df,ticker,short_window=50,long_window=200):

    close=get_close(df,ticker)
    
    short_ma=close.rolling(window=short_window).mean()
    long_ma=close.rolling(window=long_window).mean()
    signal=(short_ma > long_ma).astype(int)
    returns=close.pct_change().fillna(0)*signal.shift(1).fillna(0)
    equity=(1+returns).cumprod()
    
    if not equity.empty: equity=equity/equity.iloc[0]
    return equity

def rsi_strategy(df,ticker,window=14,buy_threshold=30,sell_threshold=70):
    close=get_close(df,ticker)
    delta=close.diff()
    gain=(delta.where(delta>0,0)).rolling(window=window).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=window).mean()
    
    rs=gain/loss
    rsi=100-(100/(1+rs))

    signal_values=[]
    position=0
    
    for r in rsi:
        if r<buy_threshold:
            position=1
        elif r>sell_threshold:
            position=0
        signal_values.append(position)
        
    signal=pd.Series(signal_values, index=close.index)  
    returns=close.pct_change().fillna(0)*signal.shift(1).fillna(0)
    equity=(1+returns).cumprod()
    
    if not equity.empty: equity=equity/equity.iloc[0]
    return equity