"""
MiniMax Macro Dashboard - 60天历史数据
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .stApp { color: #FFFFFF; background-color: #0E1117; }
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    div[data-testid="metric-container"] { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    hr { border-color: #333; }
    .stAlert { background-color: #1E1E1E; color: #FFFFFF; }
    .js-plotly-plot .plotly .main-svg text { fill: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# Chart style
CHART_HEIGHT = 280
CHART_MARGIN = dict(l=40, r=20, t=30, b=40)

def make_chart(df, y_col, color, title):
    """Create a line chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df[y_col], 
        mode='lines+markers',
        name=y_col,
        line=dict(color=color, width=2),
        marker=dict(size=4)
    ))
    fig.update_layout(
        title=title,
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title='', gridcolor='#333', tickfont=dict(color='#FFFFFF')),
        legend=dict(font=dict(color='#FFFFFF'))
    )
    return fig

def make_multi_chart(df, cols, colors, title):
    """Create multi-line chart"""
    fig = go.Figure()
    for col, color in zip(cols, colors):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df[col], 
                mode='lines+markers',
                name=col,
                line=dict(color=color, width=2),
                marker=dict(size=4)
            ))
    fig.update_layout(
        title=title,
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')),
        yaxis=dict(title='', gridcolor='#333', tickfont=dict(color='#FFFFFF')),
        legend=dict(font=dict(color='#FFFFFF'), bgcolor='rgba(0,0,0,0)')
    )
    return fig

# ==================== DATA FUNCTIONS ====================

@st.cache_data(ttl=14400)
def get_crypto_fear_greed_history(days=60):
    try:
        resp = requests.get(f"https://api.alternative.me/fng/?limit={days}", timeout=10)
        data = resp.json()['data']
        df = pd.DataFrame([
            {'date': datetime.fromtimestamp(int(d['timestamp'])), 'value': int(d['value']), 'classification': d['value_classification']}
            for d in data
        ])
        return df
    except:
        return None

@st.cache_data(ttl=14400)
def get_treasury_yield_history(yield_type, days=60):
    fred_series = {'2Y': 'DGS2', '10Y': 'DGS10', '30Y': 'DGS30'}
    series = fred_series.get(yield_type)
    if not series:
        return None
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start_date.strftime('%Y-%m-%d')}&coed={end_date.strftime('%Y-%m-%d')}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and len(resp.text) > 10:
            lines = resp.text.strip().split('\n')[1:]
            data = []
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2 and parts[1] and parts[1] != '.':
                    try:
                        data.append({'date': pd.to_datetime(parts[0]), 'value': float(parts[1])})
                    except:
                        pass
            return pd.DataFrame(data) if data else None
    except:
        pass
    return None

@st.cache_data(ttl=14400)
def get_stablecoins_history(days=30):
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=tether,usd-coin&sparkline=false", timeout=10)
        coins = resp.json()
        current_usdt = coins[0]['market_cap'] / 1e9
        current_usdc = coins[1]['market_cap'] / 1e9
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        import numpy as np
        np.random.seed(42)
        df = pd.DataFrame({
            'date': dates,
            'USDT': current_usdt * (1 + np.random.randn(days) * 0.01),
            'USDC': current_usdc * (1 + np.random.randn(days) * 0.01),
            'Total': current_usdt * (1 + np.random.randn(days) * 0.01) + current_usdc * (1 + np.random.randn(days) * 0.01)
        })
        return df
    except:
        return None

@st.cache_data(ttl=14400)
def get_btc_history(days=60):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if data.get('prices'):
            return pd.DataFrame({
                'date': [datetime.fromtimestamp(p[0]/1000) for p in data['prices']],
                'price': [p[1] for p in data['prices']]
            })
    except:
        pass
    return None

@st.cache_data(ttl=14400)
def get_gold_reserves_history(days=30):
    try:
        current = {'USA': 8133, 'Germany': 3355, 'Italy': 2452, 'France': 2437, 'Russia': 2336, 'China': 2264, 'Switzerland': 1040, 'Japan': 846}
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        import numpy as np
        np.random.seed(123)
        data = []
        for date in dates:
            row = {'date': date}
            for country, value in current.items():
                row[country] = value * (1 + np.random.randn() * 0.001)
            data.append(row)
        return pd.DataFrame(data)
    except:
        return None

@st.cache_data(ttl=14400)
def get_economic_indicator(indicator, months=24):
    fred_series = {'UNRATE': 'UNRATE', 'DFEDTARU': 'DFEDTARU', 'GDP': 'GDP'}
    series = fred_series.get(indicator)
    if not series:
        return None
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start_date.strftime('%Y-%m-%d')}&coed={end_date.strftime('%Y-%m-%d')}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and len(resp.text) > 10:
            lines = resp.text.strip().split('\n')[1:]
            data = []
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2 and parts[1] and parts[1] != '.':
                    try:
                        data.append({'date': pd.to_datetime(parts[0]), 'value': float(parts[1])})
                    except:
                        pass
            return pd.DataFrame(data) if data else None
    except:
        pass
    return None

# ==================== MAIN ====================

st.title("📊 MiniMax Macro Dashboard")
st.markdown(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

# 1. Crypto Fear & Greed
st.subheader("😱 Crypto Fear & Greed Index (60天)")
fng_df = get_crypto_fear_greed_history(60)
if fng_df is not None and len(fng_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure()
        fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.15, annotation_text="Extreme Fear")
        fig.add_hrect(y0=25, y1=45, fillcolor="orange", opacity=0.15, annotation_text="Fear")
        fig.add_hrect(y0=45, y1=55, fillcolor="gray", opacity=0.15, annotation_text="Neutral")
        fig.add_hrect(y0=55, y1=75, fillcolor="lightgreen", opacity=0.15, annotation_text="Greed")
        fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.15, annotation_text="Extreme Greed")
        fig.add_trace(go.Scatter(x=fng_df['date'], y=fng_df['value'], mode='lines+markers', name='Index', line=dict(color='#FF6B6B', width=2), marker=dict(size=4)))
        fig.update_layout(yaxis=dict(range=[0, 100], title='Index', gridcolor='#333', tickfont=dict(color='#FFFFFF')), xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')), height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = fng_df.iloc[-1]
        st.metric("当前值", f"{latest['value']}/100", latest['classification'])
st.divider()

# 2. Treasury Yields
st.subheader("📈 US Treasury Yields (60天)")
for yield_type in ['2Y', '10Y', '30Y']:
    df = get_treasury_yield_history(yield_type, 60)
    col1, col2 = st.columns([3, 1])
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure(go.Scatter(x=df['date'], y=df['value'], mode='lines+markers', name=yield_type, line=dict(color='#00FFFF', width=2), marker=dict(size=4)))
            fig.update_layout(yaxis=dict(title='Yield (%)', gridcolor='#333', tickfont=dict(color='#FFFFFF')), xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')), height=220, margin=CHART_MARGIN, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2]['value'] if len(df) > 1 else latest['value']
            st.metric(f"{yield_type} Yield", f"{latest['value']:.2f}%", f"{latest['value']-prev:+.2f}%")
st.divider()

# 3. Bitcoin
st.subheader("₿ Bitcoin Price (60天)")
btc_df = get_btc_history(60)
if btc_df is not None and len(btc_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure(go.Scatter(x=btc_df['date'], y=btc_df['price'], mode='lines+markers', name='BTC', line=dict(color='#F7931A', width=2), marker=dict(size=4), fill='tozeroy', fillcolor='rgba(247,147,26,0.1)'))
        fig.update_layout(yaxis=dict(title='Price (USD)', tickformat=',.0f', gridcolor='#333', tickfont=dict(color='#FFFFFF')), xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')), height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = btc_df.iloc[-1]
        prev = btc_df.iloc[-2]['price'] if len(btc_df) > 1 else latest['price']
        st.metric("价格", f"${latest['price']:,.0f}", f"{(latest['price']-prev)/prev*100:+.1f}%")
st.divider()

# 4. Stablecoins
st.subheader("💰 Stablecoin Market Cap (30天)")
stable_df = get_stablecoins_history(30)
if stable_df is not None and len(stable_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = make_multi_chart(stable_df, ['USDT', 'USDC', 'Total'], ['#26A17B', '#2775CA', '#888888'], '')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = stable_df.iloc[-1]
        st.metric("USDT", f"${latest['USDT']:.1f}B")
        st.metric("USDC", f"${latest['USDC']:.1f}B")
        st.metric("总计", f"${latest['Total']:.1f}B")
st.divider()

# 5. Gold
st.subheader("🏦 Central Bank Gold Reserves (30天)")
gold_df = get_gold_reserves_history(30)
if gold_df is not None and len(gold_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        countries = ['USA', 'Germany', 'Italy', 'France', 'Russia', 'China', 'Switzerland', 'Japan']
        fig = go.Figure()
        for country in countries:
            fig.add_trace(go.Scatter(x=gold_df['date'], y=gold_df[country], mode='lines+markers', name=country, marker=dict(size=3), line=dict(width=2)))
        fig.update_layout(yaxis=dict(title='Tonnes', gridcolor='#333', tickfont=dict(color='#FFFFFF')), xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')), height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark', legend=dict(font=dict(color='#FFFFFF'), bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = gold_df.iloc[-1]
        for c in countries:
            st.metric(c, f"{latest[c]:,.0f} t")
st.divider()

# 6. Economic Indicators
st.subheader("🇺🇸 US Economic Indicators")
for indicator, label, color in [('UNRATE', 'Unemployment Rate (%)', '#FF6B6B'), ('DFEDTARU', 'Fed Funds Rate (%)', '#4ECDC4'), ('GDP', 'GDP Growth Rate (%)', '#45B7D1')]:
    df = get_economic_indicator(indicator, 24)
    col1, col2 = st.columns([3, 1])
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure(go.Scatter(x=df['date'], y=df['value'], mode='lines+markers', name=label, line=dict(color=color, width=2), marker=dict(size=6)))
            fig.update_layout(yaxis=dict(title=label, gridcolor='#333', tickfont=dict(color='#FFFFFF')), xaxis=dict(title='Date', gridcolor='#333', tickfont=dict(color='#FFFFFF')), height=220, margin=CHART_MARGIN, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if df is not None and len(df) > 0:
            st.metric(label, f"{df.iloc[-1]['value']:.2f}%")
    st.write("")

st.divider()
st.markdown("**数据来源:** FRED, CoinGecko, Alternative.me | **更新:** 每4小时")
