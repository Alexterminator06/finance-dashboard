import streamlit as st
import plotly.express as px
from .data import load_asset
from .strategies import buy_and_hold, momentum

def quant_a_dashboard():
    ticker = st.sidebar.selectbox("Asset", ["AAPL", "BTC-USD", "EURUSD=X"])
    lookback = st.sidebar.slider("Momentum lookback", 5, 60, 20)

    df = load_asset(ticker)
    equity_bh = buy_and_hold(df)
    equity_mom = momentum(df, lookback)

    fig = px.line(df, y="close", title="Price + Strategies")
    fig.add_scatter(x=df.index, y=equity_bh, name="Buy & Hold")
    fig.add_scatter(x=df.index, y=equity_mom, name="Momentum")

    st.plotly_chart(fig, use_container_width=True)
