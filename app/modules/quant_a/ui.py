# app/modules/quant_a/ui.py
import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import pandas as pd
from datetime import datetime
from modules.quant_a.strategies import buy_and_hold, momentum
from app.daily_report import generate_daily_report


def quant_a_dashboard():
    st.title("📈 Quant A - Single Asset Analysis")

    # Choix de l'actif
    tickers = ["AAPL", "BTC-USD", "EURUSD=X"]
    ticker = st.selectbox("Select ticker", tickers)

    # Téléchargement des données
    df = yf.download(ticker, period="6mo", interval="1d", group_by='ticker', auto_adjust=True)

    # Curseur lookback pour Momentum
    lookback = st.sidebar.slider("Momentum lookback", 5, 30, 10)

    # Calcul des stratégies
    equity_bh = buy_and_hold(df, ticker)
    equity_mom = momentum(df, ticker, lookback)

    # Graphiques
    fig = px.line(df[ticker], y='Close', title=f"{ticker} Price + Strategies")
    fig.add_scatter(x=equity_bh.index, y=equity_bh.values, mode='lines', name='Buy & Hold')
    fig.add_scatter(x=equity_mom.index, y=equity_mom.values, mode='lines', name='Momentum')
    st.plotly_chart(fig)

    # -----------------------
    # Daily Report Section
    # -----------------------
    st.header("📊 Daily Report")
    daily_report = generate_daily_report([ticker])
    st.dataframe(daily_report)

    # Option téléchargement CSV
    st.download_button(
        label="Download report as CSV",
        data=daily_report.to_csv(index=False),
        file_name=f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime='text/csv'
    )
