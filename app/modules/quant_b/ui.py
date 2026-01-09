import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from modules.quant_b.data import load_assets
from modules.quant_b.portfolio import calculate_portfolio
from app.common.metrics import calculate_correlation,portfolio_volatility,sharpe_ratio,max_drawdown
from app.daily_report import generate_daily_report

def quant_b_dashboard():
    st.header("Multi-Asset Portfolio Manager")

    #1
    with st.expander("Portfolio Configuration",expanded=True):
        c1,c2,c3=st.columns(3)
        with c1:
            initial_capital=st.number_input("Total Investment ($)",min_value=1000,value=50000,step=1000)
        with c2:
            default_start=pd.to_datetime("2023-01-01")
            start_date=st.date_input("Start Date",value=default_start,key="qb_date_picker")
        with c3:
            allocation_type=st.radio("Allocation Strategy",["Equal Weight","Custom Weights"],horizontal=True)

        default_tickers=["AAPL","MSFT","GOOGL","BTC-USD"]
        tickers=st.multiselect(
            "Select Assets (Min 3 recommended)",
            ["AAPL","MSFT","GOOGL","AMZN","TSLA","BTC-USD","ETH-USD","GLD","EURUSD=X"],
            default_tickers,
            key="qb_asset_selector"
        )

        if len(tickers)<2:
            st.warning("Please select at least 2 assets.")
            return

        custom_weights=None
        if allocation_type=="Custom Weights":
            st.markdown("Asset Weights")
            weights_input=[]
            cols=st.columns(len(tickers)) 
            for i,t in enumerate(tickers):
                col_idx=i%len(cols)
                with cols[col_idx]:
                    w=st.slider(f"{t}",0.0,1.0,1.0/len(tickers),key=f"w_{t}")
                    weights_input.append(w)
            custom_weights=weights_input

    #2
    with st.spinner(f"Simulating portfolio from {start_date}..."):
        df=load_assets(tickers,start_date)
        
        if df.empty:
            st.error("No data found. Check your date range or internet connection.")
            return
            
        portfolio_value=calculate_portfolio(df,weights=custom_weights)
        if portfolio_value.empty:
            st.error("Insufficient data. Please select an earlier date (at least 2 days ago).")
            return

    #3
    st.subheader("Financial Overview")
    end_val=portfolio_value.iloc[-1]
    final_bal=initial_capital*end_val
    pnl=final_bal-initial_capital
    vol=portfolio_volatility(portfolio_value)*100

    m1,m2,m3,m4=st.columns(4)
    m1.metric("Final Balance",f"${final_bal:,.0f}")
    m2.metric("Total PnL",f"${pnl:,.0f}",delta=f"{(end_val-1)*100:.2f}%")
    m3.metric("Annual Volatility",f"{vol:.2f}%")
    m4.metric("Assets Count",f"{len(tickers)}")
    
    st.markdown("---")

    #4
    st.subheader("Portfolio Performance")

    df_norm=df/df.iloc[0]
    plot_data=df_norm.copy()
    plot_data['PORTFOLIO']=portfolio_value

    fig=px.line(plot_data,title="Assets vs Portfolio Evolution (Normalized Base 1.0)")
    fig.update_traces(selector=dict(name='PORTFOLIO'),line=dict(width=4,color='white'))
    st.plotly_chart(fig,use_container_width=True)

    #5
    with st.expander("View Correlation Matrix"):
        corr=calculate_correlation(df)
        fig_corr=px.imshow(corr,text_auto=".2f",aspect="auto",color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_corr,use_container_width=True)

    #6
    with st.expander("View Technical Metrics"):
        port_ret=portfolio_value.pct_change().dropna()
        sharpe=sharpe_ratio(port_ret)
        dd=max_drawdown(portfolio_value)
        active_days=port_ret[port_ret!=0]
        if len(active_days)>0:
            win_rate=(active_days[active_days>0].count()/len(active_days))*100
        else:
            win_rate=0.0
        c1,c2,c3=st.columns(3)
        c1.metric("Sharpe Ratio",f"{sharpe:.2f}",help="Risk-adjusted return")
        c2.metric("Max Drawdown",f"{dd:.2%}",help="Maximum loss from peak",delta_color="inverse")
        c3.metric("Daily Win Rate",f"{win_rate:.1f}%",help="% of positive days")
    with st.expander("View Daily Report"):
        st.dataframe(generate_daily_report(tickers), use_container_width=True)