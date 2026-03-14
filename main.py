import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from signals import get_spy_data

st.set_page_config(layout="wide", page_title="S&P 500 Trade Signals")
st.title("S&P 500 Trade Signal Dashboard")

# Sidebar — date range selector
with st.sidebar:
    st.header("Settings")
    period = st.selectbox(
        "Time Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=4,
    )

df = get_spy_data(period=period)

# --- Signal summary metrics ---
longs = df[df['Signal'] == 'LONG']
shorts = df[df['Signal'] == 'SHORT']
signals_all = df[df['Signal'] != '']
last_signal_row = signals_all.iloc[-1] if not signals_all.empty else None
current_rsi = df['RSI'].iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("LONG Signals", len(longs))
col2.metric("SHORT Signals", len(shorts))
if last_signal_row is not None:
    last_date = last_signal_row.name.strftime("%Y-%m-%d")
    col3.metric("Last Signal", f"{last_signal_row['Signal']} ({last_date})")
else:
    col3.metric("Last Signal", "None")
col4.metric("Current RSI", f"{current_rsi:.1f}")

st.divider()

# --- Price chart with Buy/Sell markers ---
st.subheader("Price Chart with Trade Signals")

fig_price = go.Figure()

fig_price.add_trace(go.Scatter(
    x=df.index,
    y=df['Close'],
    mode='lines',
    name='SPY Close',
    line=dict(color='royalblue', width=1.5),
))

if not longs.empty:
    fig_price.add_trace(go.Scatter(
        x=longs.index,
        y=longs['Close'],
        mode='markers',
        name='LONG',
        marker=dict(symbol='triangle-up', color='green', size=10),
    ))

if not shorts.empty:
    fig_price.add_trace(go.Scatter(
        x=shorts.index,
        y=shorts['Close'],
        mode='markers',
        name='SHORT',
        marker=dict(symbol='triangle-down', color='red', size=10),
    ))

fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400,
    margin=dict(l=0, r=0, t=10, b=0),
)

st.plotly_chart(fig_price, use_container_width=True)

# --- RSI chart ---
st.subheader("RSI")

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='orange')))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
fig_rsi.update_layout(
    yaxis=dict(range=[0, 100]),
    height=250,
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig_rsi, use_container_width=True)

# --- MACD chart ---
st.subheader("MACD")

fig_macd = make_subplots(rows=1, cols=1)

fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='Signal Line', line=dict(color='orange', dash='dash')))

colors = ['green' if v >= 0 else 'red' for v in df['MACD_Diff']]
fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], name='Histogram', marker_color=colors, opacity=0.6))

fig_macd.update_layout(
    height=280,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

st.plotly_chart(fig_macd, use_container_width=True)

# --- Recent signals table ---
st.subheader("Recent Trade Signals")
recent = df[df['Signal'] != ''][['Close', 'RSI', 'MACD', 'Signal']].tail(10)
recent.index = recent.index.strftime("%Y-%m-%d")
st.dataframe(recent, use_container_width=True)
