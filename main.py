import yfinance as yf
import pandas as pd
import ta

def get_spy_data(period="2y"):
    spy = yf.Ticker("SPY")
    hist = spy.history(period=period)
    hist.dropna(inplace=True)
    hist['RSI'] = ta.momentum.RSIIndicator(close=hist['Close']).rsi()
    hist['Signal'] = hist['RSI'].apply(lambda r: 'LONG' if r < 30 else 'SHORT' if r > 70 else '')
    return hist

if __name__ == "__main__":
    df = get_spy_data()
    print(df[df['Signal'] != ''].tail())