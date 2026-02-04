import yfinance as yf
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

def predict_future(ticker, days=30):
    """
    Entraîne une IA sur les données historiques et prédit les X prochains jours.
    Renvoie : le modèle (pour le graphique) et les données prévues.
    """
    ticker = ticker.upper()
    
    # 1. Récupérer 2 ans d'historique (pour que l'IA apprenne les saisons)
    data = yf.download(ticker, period="2y", interval="1d", progress=False)
    
    if data.empty:
        return None, None, "Pas de données trouvées."
    
    # 2. Préparer les données pour Prophet
    # Prophet veut deux colonnes exactes : 'ds' (date) et 'y' (valeur)
    df_train = data.reset_index()[['Date', 'Close']]
    df_train.columns = ['ds', 'y']
    
    # Petit nettoyage de fuseau horaire pour éviter les erreurs
    df_train['ds'] = df_train['ds'].dt.tz_localize(None)

    # 3. Création et Entraînement de l'IA
    # daily_seasonality=True aide pour les actions
    m = Prophet(daily_seasonality=True) 
    m.fit(df_train)
    
    # 4. Créer le futur (les dates vides qu'on veut prédire)
    future = m.make_future_dataframe(periods=days)
    
    # 5. Prédire !
    forecast = m.predict(future)
    
    return m, forecast, "Succès"