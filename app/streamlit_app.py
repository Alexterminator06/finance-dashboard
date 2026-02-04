import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import yfinance as yf
from prophet.plot import plot_plotly

# CONFIGURATION CHEMIN
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(root_dir)

from core.portfolio_manager import get_cash_balance, add_cash, buy_stock_amount, get_portfolio_positions
from core.predictor import predict_future

st.set_page_config(page_title="Trading Bot Pro", layout="wide")
st.title("🤖 Trading Bot Pro & Scanner")

# --- FONCTION UTILITAIRE : CALCUL DU RSI ---
def calculate_rsi(ticker, periods=14):
    """Calcule le RSI (Relative Strength Index) sur 14 jours"""
    try:
        # On récupère un peu plus de données pour lisser le calcul
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)['Close']
        
        # Gestion format Series vs DataFrame
        if isinstance(data, pd.DataFrame):
            data = data.iloc[:, 0] # On prend la première colonne
            
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] # On retourne le dernier RSI connu
    except:
        return 50.0 # Valeur neutre par défaut en cas d'erreur

# --- ONGLETS ---
tab1, tab2 = st.tabs(["💼 Mon Portefeuille", "📡 Super Scanner IA"])

# ==========================================
# ONGLET 1 : GESTION DU PORTEFEUILLE
# ==========================================
with tab1:
    cash = get_cash_balance()
    portfolio = get_portfolio_positions()

    valeur_actions = 0.0
    cout_total = 0.0
    details = []

    if portfolio:
        tickers = list(portfolio.keys())
        try:
            data = yf.download(tickers, period="1d", progress=False)['Close']
            last = data.iloc[-1]
            if isinstance(last, pd.Series):
                prices = last.to_dict()
            else:
                prices = {tickers[0]: last}
        except:
            prices = {}

        for t, d in portfolio.items():
            if t in prices:
                p = float(prices[t])
                v = d['quantity'] * p
                c = d['cost']
                valeur_actions += v
                cout_total += c
                details.append({
                    "Ticker": t,
                    "Qté": f"{d['quantity']:.4f}",
                    "Prix Achat": f"{(c/d['quantity']):.2f} €",
                    "Prix Actuel": f"{p:.2f} €",
                    "P&L (€)": v - c
                })

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash", f"{cash:,.2f} €")
    c2.metric("Actions", f"{valeur_actions:,.2f} €", delta=f"{valeur_actions - cout_total:+.2f} €")
    c3.metric("Total", f"{cash + valeur_actions:,.2f} €")

    st.divider()
    
    # ACHAT
    col_achat, col_tab = st.columns([1, 2])
    with col_achat:
        st.subheader("Acheter")
        with st.form("achat"):
            tick = st.text_input("Symbole", "AAPL").upper()
            amt = st.number_input("Montant (€)", 100.0)
            if st.form_submit_button("Valider"):
                ok, msg = buy_stock_amount(tick, amt)
                if ok:
                    st.success("Ordre exécuté")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
                    
    with col_tab:
        st.subheader("Positions")
        if details:
            df = pd.DataFrame(details)
            st.dataframe(
                df.style.format({"P&L (€)": "{:+,.2f} €"})
                  .applymap(lambda v: f'color: {"green" if v > 0 else "red"}', subset=['P&L (€)']),
                use_container_width=True
            )

# ==========================================
# ONGLET 2 : SUPER SCANNER
# ==========================================
with tab2:
    st.header("🧠 Scanner & Intelligence Artificielle")
    
    # Choix du mode
    mode = st.radio("Mode :", ["🔍 Analyse unique", "🌍 Scanner Global (Liste Perso)"], horizontal=True)

    if mode == "🔍 Analyse unique":
        col_search, col_res = st.columns([1, 3])
        with col_search:
            target = st.text_input("Symbole à analyser", "NVDA").upper()
            days = st.slider("Horizon (Jours)", 7, 90, 30)
            run_pred = st.button("Lancer l'analyse")
        
        with col_res:
            if run_pred:
                with st.spinner(f"Analyse de {target}..."):
                    model, forecast, status = predict_future(target, days)
                    rsi = calculate_rsi(target)
                    
                    if model:
                        st.metric("RSI (Indicateur Technique)", f"{rsi:.1f}", help="< 30 : Sur-vendu (Bon marché) | > 70 : Sur-acheté (Cher)")
                        fig = plot_plotly(model, forecast)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(status)

    else: # MODE SCANNER GLOBAL
        st.info("Entre les symboles séparés par des virgules (ex: CAC 40, Crypto, Tech US...)")
        
        # PISTE 1 : INPUT UNIVERSEL
        default_list = "AAPL, NVDA, TSLA, MSFT, BTC-USD, ETH-USD, MC.PA, TTE.PA"
        user_list = st.text_area("Liste des actions :", default_list)
        
        if st.button("🚀 LANCER LE SCAN MULTI-CRITÈRES"):
            tickers_to_scan = [t.strip().upper() for t in user_list.split(",") if t.strip()]
            results = []
            
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(tickers_to_scan):
                progress_bar.progress((i + 1) / len(tickers_to_scan), text=f"Analyse IA + RSI sur {ticker}...")
                
                try:
                    # 1. PRÉDICTION IA (FUTUR)
                    _, forecast, _ = predict_future(ticker, days=30)
                    
                    # 2. ANALYSE RSI (PASSÉ)
                    rsi_val = calculate_rsi(ticker)
                    
                    if forecast is not None:
                        start = forecast.iloc[-31]['yhat']
                        end = forecast.iloc[-1]['yhat']
                        growth = ((end - start) / start) * 100
                        
                        # --- ALGORITHME DE DÉCISION ---
                        # On combine l'IA et le RSI pour un score
                        signal = "NEUTRE"
                        score = 0