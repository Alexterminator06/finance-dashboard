import streamlit as st
from modules.quant_a.ui import quant_a_dashboard
from modules.quant_b.ui import quant_b_dashboard



st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("Finance Dashboard")

tab1, tab2 = st.tabs(["Single Asset", "Portfolio"])

with tab1:
    quant_a_dashboard()

with tab2:
    quant_b_dashboard()





