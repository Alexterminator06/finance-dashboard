import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime,timedelta
import pandas as pd
from common.metrics import sharpe_ratio,max_drawdown
from modules.quant_a.strategies import (
    buy_and_hold,momentum,bollinger_bands_strategy,
    dual_sma_crossover,rsi_strategy
)
from modules.quant_a.prediction import predict_next_day
from app.daily_report import generate_daily_report
def quant_a_dashboard():
    #1
    with st.container():
        st.subheader("Configuration")
        
        c1,c2,c3,c4=st.columns([1,1,1,1.5])
        
        with c1:
            tickers=["AAPL","BTC-USD","EURUSD=X","GOOGL","MSFT","NVDA","GC=F"]
            ticker=st.selectbox("Asset",tickers)
        
        with c2:
            start_date=st.date_input("Start Date",value=pd.to_datetime("2023-01-01"))

        with c3:
            initial_capital=st.number_input("Capital ($)",min_value=1000,value=10000,step=1000)
            
        with c4:
            strategy_choice=st.selectbox("Strategy Model",["Momentum","Bollinger Bands","Dual SMA","RSI"])
        
        with st.expander(f"Settings for {strategy_choice}",expanded=True):
            start_str=start_date.strftime('%Y-%m-%d')
            df=yf.download(ticker,start=start_str,interval="1d",group_by='ticker',auto_adjust=True)
            
            col_p1,col_p2,col_p3=st.columns(3)
            equity_strategy=None
            
            if strategy_choice=="Momentum":
                with col_p1: lookback=st.slider("Lookback (days)",5,60,15)
                equity_strategy=momentum(df,ticker,lookback)
            elif strategy_choice=="Bollinger Bands":
                with col_p1: window=st.slider("MA Window",10,50,20)
                with col_p2: std_dev=st.slider("Std Dev",1.0,3.0,2.0)
                equity_strategy=bollinger_bands_strategy(df,ticker,window,std_dev)
            elif strategy_choice=="Dual SMA":
                with col_p1: short_w=st.slider("Short MA",10,100,50)
                with col_p2: long_w=st.slider("Long MA",50,300,200)
                equity_strategy=dual_sma_crossover(df,ticker,short_w,long_w)
            elif strategy_choice=="RSI":
                with col_p1: rsi_window=st.slider("Period",5,30,14)
                with col_p2: buy_thresh=st.slider("Buy Level",10,40,30)
                with col_p3: sell_thresh=st.slider("Sell Level",60,90,70)
                equity_strategy=rsi_strategy(df,ticker,rsi_window,buy_thresh,sell_thresh)

    st.markdown("---")

    if df.empty:
        st.error("No data available.")
        return

    price_series=None
    if isinstance(df.columns,pd.MultiIndex) and ticker in df.columns:
        price_series=df[ticker]['Close']
    elif 'Close' in df.columns:
        price_series=df['Close']
    else:
        price_series=df.iloc[:,0]

    equity_bh=buy_and_hold(df,ticker)

    #2
    
    final_equity=equity_strategy.iloc[-1]
    final_balance=initial_capital*final_equity
    net_profit=final_balance-initial_capital
    
    perf_strat_pct=(final_equity-1)*100
    perf_bh_pct=(equity_bh.iloc[-1]-1)*100
    delta_perf=perf_strat_pct-perf_bh_pct

    try:
        pred_price,confidence=predict_next_day(df)
        delta_ml=((pred_price-price_series.iloc[-1])/price_series.iloc[-1])*100
    except:
        pred_price=None

    st.subheader("Financial Overview")
    kpi1,kpi2,kpi3,kpi4=st.columns(4)
    
    kpi1.metric("Final Balance",f"${final_balance:,.0f}")
    kpi2.metric("Total Return",f"{perf_strat_pct:.2f}%",delta=f"{delta_perf:.2f}% vs B&H")
    kpi3.metric("Net Profit",f"${net_profit:,.0f}")
    
    if pred_price:
        kpi4.metric("AI Prediction",f"${pred_price:.2f}",delta=f"{delta_ml:.2f}%")
    else:
        kpi4.metric("AI Prediction","N/A")
    st.markdown("---")
    #3
    st.subheader("Performance Chart")
    fig=make_subplots(specs=[[{"secondary_y": True}]])


    fig.add_trace(go.Scatter(x=price_series.index,y=price_series,name="History",line=dict(color='rgba(50,100,255,0.5)',width=1)),secondary_y=False)
    

    if pred_price:
        last_date=price_series.index[-1]
        next_date=last_date+timedelta(days=1)
        last_val=price_series.iloc[-1]
        

        pred_x=[last_date,next_date]
        pred_y=[last_val,pred_price]
        
        fig.add_trace(
            go.Scatter(
                x=pred_x,
                y=pred_y,
                mode='lines+markers',
                name='AI Forecast',
                line=dict(color='#FF4B4B',width=2,dash='dot'),
                marker=dict(symbol='circle',size=6,color='#FF4B4B')
            ),
            secondary_y=False
        )


    fig.add_trace(go.Scatter(x=equity_strategy.index,y=equity_strategy,name=f"Strategy ({strategy_choice})",line=dict(color='#00CC96',width=2)),secondary_y=True)
    

    fig.add_trace(go.Scatter(x=equity_bh.index,y=equity_bh,name="Buy & Hold",line=dict(color='gray',dash='dot',width=1)),secondary_y=True)

    fig.update_layout(height=500,hovermode="x unified",legend=dict(orientation="h",y=1.1,x=0.5,xanchor="center"))
    fig.update_yaxes(title_text="Price ($)",secondary_y=False,showgrid=False)
    fig.update_yaxes(title_text="Growth (1.0=Start)",secondary_y=True,showgrid=True)
    st.plotly_chart(fig,use_container_width=True)

    #4
    with st.expander("View Technical Comparison"):
        strat_ret=equity_strategy.pct_change().dropna()
        bh_ret=equity_bh.pct_change().dropna()
        
        sharpe_strat=sharpe_ratio(strat_ret)
        sharpe_bh=sharpe_ratio(bh_ret)
        dd_strat=max_drawdown(equity_strategy)
        dd_bh=max_drawdown(equity_bh)
        
        active_days=strat_ret[strat_ret != 0]
        win_rate=(active_days[active_days > 0].count()/len(active_days)*100) if len(active_days) > 0 else 0

        m1,m2,m3=st.columns(3)
        m1.metric("Sharpe Ratio",f"{sharpe_strat:.2f}",delta=f"{sharpe_strat-sharpe_bh:.2f} vs Market")
        m2.metric("Max Drawdown",f"{dd_strat:.2%}",delta=f"{(dd_strat-dd_bh)*100:.2f} pts vs Market",delta_color="inverse")
        m3.metric("Daily Win Rate",f"{win_rate:.1f}%")

    with st.expander("View Daily Report"):
        st.dataframe(generate_daily_report([ticker]),use_container_width=True)