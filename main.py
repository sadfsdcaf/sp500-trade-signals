import streamlit as st
import yfinance as yf
import pandas as pd
import ta


@st.cache_data(ttl=3600)
def get_spy_data(period="2y"):
    spy = yf.Ticker("SPY")
    hist = spy.history(period=period)
    hist.dropna(inplace=True)

    # RSI
    hist['RSI'] = ta.momentum.RSIIndicator(close=hist['Close']).rsi()
    hist['Signal'] = hist['RSI'].apply(lambda r: 'LONG' if r < 30 else 'SHORT' if r > 70 else '')

    # MACD
    macd = ta.trend.MACD(close=hist['Close'])
    hist['MACD'] = macd.macd()
    hist['MACD_Signal'] = macd.macd_signal()
    hist['MACD_Diff'] = macd.macd_diff()

    return hist


if __name__ == "__main__":
    df = get_spy_data()
    print(df[df['Signal'] != ''].tail())
