import streamlit as st
import pandas as pd
from main import get_spy_data

st.set_page_config(layout="wide", page_title="S&P 500 Trade Signals")

st.title("S&P 500 Trade Signal Dashboard")
df = get_spy_data()

st.line_chart(df['Close'])

st.markdown("### RSI & Trade Signals")
st.line_chart(df[['RSI']])

st.dataframe(df[df['Signal'] != ''][['Close', 'RSI', 'Signal']].tail(10))