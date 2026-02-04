import sqlite3
import pandas as pd
from datetime import datetime
import os
import yfinance as yf

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'portfolio.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            transaction_type TEXT,
            date TEXT
        )
    ''')

    # Note : On met quantity en REAL (nombre à virgule) et non plus INTEGER
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            action TEXT,
            quantity REAL, 
            price REAL,
            cost REAL,
            date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cash_balance():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT amount FROM cash", conn)
        return df['amount'].sum() if not df.empty else 0.0
    finally:
        conn.close()

def add_cash(amount):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO cash (amount, transaction_type, date) VALUES (?, ?, ?)", 
                 (amount, 'DEPOSIT', date))
    conn.commit()
    conn.close()

# --- C'est ICI que ça change ---
def buy_stock_amount(ticker, amount_to_invest):
    """Acheter pour un montant précis (ex: 1000€ d'Apple)"""
    init_db()
    ticker = ticker.upper()
    
    # 1. Vérifier qu'on a le cash
    balance = get_cash_balance()
    if balance < amount_to_invest:
        return False, f"❌ Fonds insuffisants ({balance:.2f}€) pour investir {amount_to_invest}€."

    # 2. Récupérer le prix
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        if history.empty:
            return False, f"❌ Ticker '{ticker}' introuvable."
        current_price = history['Close'].iloc[-1]
    except Exception as e:
        return False, f"❌ Erreur connexion : {e}"
    
    # 3. Calcul magique des fractions
    quantity = amount_to_invest / current_price
    
    # 4. Transaction
    conn = sqlite3.connect(DB_PATH)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # On enregistre la quantité précise (ex: 4.523 actions)
    conn.execute('''
        INSERT INTO trades (ticker, action, quantity, price, cost, date) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ticker, 'BUY', quantity, current_price, amount_to_invest, date))
    
    # On retire l'argent
    conn.execute("INSERT INTO cash (amount, transaction_type, date) VALUES (?, ?, ?)", 
                 (-amount_to_invest, 'BUY_STOCK', date))
    
    conn.commit()
    conn.close()
    
    return True, f"✅ Investi {amount_to_invest}€ sur {ticker} (Obtenu : {quantity:.4f} actions)"

def get_portfolio_positions():
    """
    Renvoie un dictionnaire complet : 
    {'AAPL': {'quantity': 5.0, 'total_cost': 1000.0}, ...}
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    # On récupère quantité ET coût (cost)
    df = pd.read_sql_query("SELECT ticker, quantity, cost FROM trades", conn)
    conn.close()
    
    if df.empty:
        return {}

    # On regroupe par Ticker en sommant les quantités et les coûts
    summary = df.groupby('ticker')[['quantity', 'cost']].sum()
    
    # On convertit en dictionnaire facile à lire
    # 'index' permet d'avoir : {Ticker: {col1: val, col2: val}}
    return summary[summary['quantity'] > 0].to_dict('index')