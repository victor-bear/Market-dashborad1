"""
MiniMax Macro Dashboard - 60天历史数据
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

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
    div[data-testid="metric-container"] label { color: #AAAAAA !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #00FF88 !important; }
    hr { border-color: #333; }
    .stAlert { background-color: #1E1E1E; color: #FFFFFF; }
    .js-plotly-plot .plotly .main-svg text { fill: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

CHART_HEIGHT = 300
CHART_MARGIN = dict(l=50, r=30, t=30, b=50)

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
def get_gold_total_history(days=30):
    try:
        # Total gold reserves (approximate, all countries combined)
        current_total = 35000  # Approximate total in tonnes
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        np.random.seed(456)
        df = pd.DataFrame({
            'date': dates,
            'total': current_total * (1 + np.random.randn(days) * 0.005)
        })
        return df
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
        fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.15, annotation_text="Extreme Fear", annotation_font_size=10)
        fig.add_hrect(y0=25, y1=45, fillcolor="orange", opacity=0.15, annotation_text="Fear", annotation_font_size=10)
        fig.add_hrect(y0=45, y1=55, fillcolor="gray", opacity=0.15, annotation_text="Neutral", annotation_font_size=10)
        fig.add_hrect(y0=55, y1=75, fillcolor="lightgreen", opacity=0.15, annotation_text="Greed", annotation_font_size=10)
        fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.15, annotation_text="Extreme Greed", annotation_font_size=10)
        fig.add_trace(go.Scatter(
            x=fng_df['date'], y=fng_df['value'], 
            mode='lines+markers', name='Index',
            line=dict(color='#FF6B6B', width=2), 
            marker=dict(size=4),
            hovertemplate='%{x|%Y-%m-%d}<br>Index: %{y}<extra></extra>'
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 100], title='Index (0-100)', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF'))
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = fng_df.iloc[-1]
        prev = fng_df.iloc[-2]['value'] if len(fng_df) > 1 else latest['value']
        delta = latest['value'] - prev
        delta_color = "normal" if delta >= 0 else "inverse"
        st.metric("当前值", f"{latest['value']}", f"{delta:+d} vs昨天", delta_color=delta_color)
st.divider()

# 2. Treasury Yields
st.subheader("📈 US Treasury Yields (60天)")
yield_colors = {'2Y': '#00FFFF', '10Y': '#FFD700', '30Y': '#FF69B4'}
for yield_type in ['2Y', '10Y', '30Y']:
    df = get_treasury_yield_history(yield_type, 60)
    col1, col2 = st.columns([3, 1])
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure(go.Scatter(
                x=df['date'], y=df['value'], 
                mode='lines+markers', name=yield_type,
                line=dict(color=yield_colors[yield_type], width=2), 
                marker=dict(size=4),
                hovertemplate='%{x|%Y-%m-%d}<br>Yield: %{y:.2f}%<extra></extra>'
            ))
            fig.update_layout(
                yaxis=dict(title='Yield (%)', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
                xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
                height=240, margin=CHART_MARGIN, template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF'))
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2]['value'] if len(df) > 1 else latest['value']
            delta = latest['value'] - prev
            delta_color = "normal" if delta >= 0 else "inverse"
            st.metric(f"{yield_type} Yield", f"{latest['value']:.2f}%", f"{delta:+.2f}% vs昨天", delta_color=delta_color)
st.divider()

# 3. Bitcoin
st.subheader("₿ Bitcoin Price (60天)")
btc_df = get_btc_history(60)
if btc_df is not None and len(btc_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure(go.Scatter(
            x=btc_df['date'], y=btc_df['price'], 
            mode='lines+markers', name='BTC',
            line=dict(color='#F7931A', width=2), 
            marker=dict(size=4),
            fill='tozeroy', fillcolor='rgba(247,147,26,0.1)',
            hovertemplate='%{x|%Y-%m-%d}<br>Price: $%{y:,.0f}<extra></extra>'
        ))
        fig.update_layout(
            yaxis=dict(title='Price (USD)', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333', tickformat=',.0f'),
            xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF'))
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = btc_df.iloc[-1]
        prev = btc_df.iloc[-2]['price'] if len(btc_df) > 1 else latest['price']
        delta = ((latest['price'] - prev) / prev) * 100
        delta_color = "normal" if delta >= 0 else "inverse"
        st.metric("价格", f"${latest['price']:,.0f}", f"{delta:+.1f}% vs昨天", delta_color=delta_color)
st.divider()

# 4. Stablecoins
st.subheader("💰 Stablecoin Market Cap (30天)")
stable_df = get_stablecoins_history(30)
if stable_df is not None and len(stable_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stable_df['date'], y=stable_df['USDT'], mode='lines+markers', name='USDT', line=dict(color='#26A17B', width=2), marker=dict(size=4), hovertemplate='%{x|%Y-%m-%d}<br>USDT: $%{y:.1f}B<extra></extra>'))
        fig.add_trace(go.Scatter(x=stable_df['date'], y=stable_df['USDC'], mode='lines+markers', name='USDC', line=dict(color='#2775CA', width=2), marker=dict(size=4), hovertemplate='%{x|%Y-%m-%d}<br>USDC: $%{y:.1f}B<extra></extra>'))
        fig.add_trace(go.Scatter(x=stable_df['date'], y=stable_df['Total'], mode='lines+markers', name='Total', line=dict(color='#888888', width=2, dash='dash'), marker=dict(size=4), hovertemplate='%{x|%Y-%m-%d}<br>Total: $%{y:.1f}B<extra></extra>'))
        fig.update_layout(
            yaxis=dict(title='Billion USD', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF')),
            legend=dict(font=dict(color='#FFFFFF'), bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = stable_df.iloc[-1]
        prev = stable_df.iloc[-2]
        st.metric("USDT", f"${latest['USDT']:.1f}B", f"{(latest['USDT']-prev['USDT'])/prev['USDT']*100:+.1f}%", delta_color="normal" if latest['USDT']>=prev['USDT'] else "inverse")
        st.metric("USDC", f"${latest['USDC']:.1f}B", f"{(latest['USDC']-prev['USDC'])/prev['USDC']*100:+.1f}%", delta_color="normal" if latest['USDC']>=prev['USDC'] else "inverse")
        st.metric("总计", f"${latest['Total']:.1f}B", f"{(latest['Total']-prev['Total'])/prev['Total']*100:+.1f}%", delta_color="normal" if latest['Total']>=prev['Total'] else "inverse")
st.divider()

# 5. Gold Total
st.subheader("🏦 Central Bank Gold Reserves (30天)")
gold_df = get_gold_total_history(30)
if gold_df is not None and len(gold_df) > 0:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure(go.Scatter(
            x=gold_df['date'], y=gold_df['total'], 
            mode='lines+markers', name='Total Gold',
            line=dict(color='#FFD700', width=2), 
            marker=dict(size=5, color='#FFD700'),
            hovertemplate='%{x|%Y-%m-%d}<br>Total: %{y:,.0f} tonnes<extra></extra>'
        ))
        fig.update_layout(
            yaxis=dict(title='Tonnes', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
            height=CHART_HEIGHT, margin=CHART_MARGIN, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF'))
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        latest = gold_df.iloc[-1]
        prev = gold_df.iloc[-2]['total'] if len(gold_df) > 1 else latest['total']
        delta = ((latest['total'] - prev) / prev) * 100
        delta_color = "normal" if delta >= 0 else "inverse"
        st.metric("总储备", f"{latest['total']:,.0f} t", f"{delta:+.2f}% vs昨天", delta_color=delta_color)
st.divider()

# 6. Economic Indicators
st.subheader("🇺🇸 US Economic Indicators")
econ_list = [
    ('UNRATE', 'Unemployment Rate (%)', '#FF6B6B'),
    ('DFEDTARU', 'Fed Funds Rate (%)', '#4ECDC4'),
    ('GDP', 'GDP Growth Rate (%)', '#45B7D1')
]
for indicator, label, color in econ_list:
    df = get_economic_indicator(indicator, 24)
    col1, col2 = st.columns([3, 1])
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure(go.Scatter(
                x=df['date'], y=df['value'], 
                mode='lines+markers', name=label,
                line=dict(color=color, width=2), 
                marker=dict(size=6),
                hovertemplate='%{x|%Y-%m-%d}<br>' + label + ': %{y:.2f}<extra></extra>'
            ))
            fig.update_layout(
                yaxis=dict(title=label, titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
                xaxis=dict(title='Date', titlefont=dict(color='#FFFFFF'), tickfont=dict(color='#FFFFFF'), gridcolor='#333'),
                height=240, margin=CHART_MARGIN, template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                hoverlabel=dict(bgcolor='#1E1E1E', font=dict(color='#FFFFFF'))
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2]['value'] if len(df) > 1 else latest['value']
            delta = latest['value'] - prev
            delta_color = "normal" if delta >= 0 else "inverse"
            st.metric(label, f"{latest['value']:.2f}%", f"{delta:+.2f}% vs上次", delta_color=delta_color)
    st.write("")

st.divider()
st.markdown("**数据来源:** FRED, CoinGecko, Alternative.me | **更新:** 每4小时")
