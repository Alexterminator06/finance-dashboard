import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.quant_a.ui import quant_a_dashboard
from modules.quant_b.ui import quant_b_dashboard

st.set_page_config(page_title="Finance Dashboard",layout="wide")

st.title("Finance Dashboard")
col_refresh,col_void=st.columns([2,5])
with col_refresh:
    run_refresh=st.checkbox("Auto-Refresh (1 hour)",value=True)

    if run_refresh:
        # interval=millisecondes (heures*minutes*secondes*1000)
        st_autorefresh(interval=1*60*60*1000,key="data_refresh_timer")

tab1,tab2=st.tabs(["Single Asset","Portfolio"])

with tab1:
    quant_a_dashboard()

with tab2:
    quant_b_dashboard()