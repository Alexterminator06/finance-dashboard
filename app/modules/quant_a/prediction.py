import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_next_day(df):
    #I chose to use an AR model
    data=df.copy()
    series=None
    if isinstance(data.columns,pd.MultiIndex):
        for col in data.columns:
            if col[1]=='Close' or col[0]=='Close':
                series=data[col]
                break
        if series is None: series=data.iloc[:,0]
    elif 'Close' in data.columns:
        series=data['Close']
    else:
        series=data.iloc[:, 0]

    df_ml=pd.DataFrame({'Close': series})
    df_ml['Prev_Close']=df_ml['Close'].shift(1)
    df_ml=df_ml.dropna() #J'enlève la première ligne qui contient NaN

    #Je prend les 60 derniers jours pour l'entraînement
    recent_data=df_ml.tail(60)

    X=recent_data[['Prev_Close']].values
    y=recent_data['Close'].values

    model=LinearRegression()
    model.fit(X, y)

    last_known_price=np.array([[ series.iloc[-1] ]])
    predicted_price=model.predict(last_known_price)[0]

    score=model.score(X, y) #R^2

    return predicted_price, score