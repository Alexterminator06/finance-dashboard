import streamlit as st
import plotly.express as px
from .data import load_assets
from .portfolio import equal_weight_portfolio

def quant_b_dashboard():
    tickers = st.sidebar.multiselect(
        "Select assets",
        ["AAPL", "MSFT", "GOOGL", "BTC-USD", "GLD"],
        ["AAPL", "BTC-USD"]
    )

    if not tickers:
        st.warning("Choose at least one asset.")
        return

    df = load_assets(tickers)
    port = equal_weight_portfolio(df)

    fig = px.line(df, title="Asset Prices")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(port, title="Portfolio Value")
    st.plotly_chart(fig2, use_container_width=True)
