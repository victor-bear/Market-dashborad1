"""
MiniMax Macro Dashboard
实时宏观数据看板
Run: streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_crypto_fear_greed():
    """Get Crypto Fear & Greed Index"""
    try:
        resp = requests.get("https://api.alternative.me/fng/", timeout=10)
        data = resp.json()['data'][0]
        return {
            'value': int(data['value']),
            'classification': data['value_classification'],
            'timestamp': datetime.fromtimestamp(int(data['timestamp']))
        }
    except:
        return None

@st.cache_data(ttl=3600)
def get_treasury_yields():
    """Get US Treasury Yields from FRED"""
    yields = {}
    fred_series = {'2Y': 'DGS2', '10Y': 'DGS10', '30Y': 'DGS30'}
    for name, series in fred_series.items():
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2026-03-01&coed=2026-03-15"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                if len(lines) > 1:
                    val = lines[-1].split(',')[-1]
                    if val and val != '.':
                        yields[name] = float(val)
        except:
            pass
    return yields

@st.cache_data(ttl=300)
def get_stablecoins():
    """Get Stablecoin Market Cap"""
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=tether,usd-coin&sparkline=false",
            timeout=10
        )
        coins = resp.json()
        return {
            'USDT': coins[0]['market_cap'] / 1e9,
            'USDC': coins[1]['market_cap'] / 1e9,
            'total': (coins[0]['market_cap'] + coins[1]['market_cap']) / 1e9
        }
    except:
        return None

@st.cache_data(ttl=300)
def get_btc_price():
    """Get Bitcoin Price"""
    try:
        resp = requests.get("https://api.coinbase.com/v2/prices/spot?currency=USD", timeout=10)
        return float(resp.json()['data']['amount'])
    except:
        return None

@st.cache_data(ttl=3600)
def get_economic_indicators():
    """Get US Economic Indicators"""
    indicators = {}
    fred_series = {'UNRATE': 'UNRATE', 'DFEDTARU': 'DFEDTARU', 'GDP': 'GDP'}
    for name, series in fred_series.items():
        try:
            if name == 'GDP':
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2024-01-01&coed=2025-10-01"
            else:
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2025-01-01&coed=2026-02-01"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                if len(lines) > 1:
                    val = lines[-1].split(',')[-1]
                    if val and val != '.':
                        indicators[name] = float(val)
        except:
            pass
    return indicators

@st.cache_data(ttl=3600)
def get_gold_reserves():
    """Get Central Bank Gold Reserves (approximate)"""
    # World Gold Council data - approximate
    return {
        'USA': 8133,
        'Germany': 3355,
        'Italy': 2452,
        'France': 2437,
        'Russia': 2336,
        'China': 2264,
        'Switzerland': 1040,
        'Japan': 846,
    }

# Main Dashboard
st.title("📊 MiniMax Macro Dashboard")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
auto_refresh = st.checkbox("Auto-refresh (5 min)", value=True)
if auto_refresh:
    time.sleep(300)
    st.rerun()

# Row 1: Market Sentiment & Yields
col1, col2, col3, col4 = st.columns(4)

with col1:
    fng = get_crypto_fear_greed()
    if fng:
        color = 'red' if fng['value'] < 25 else 'orange' if fng['value'] < 45 else 'yellow' if fng['value'] < 55 else 'lightgreen' if fng['value'] < 75 else 'green'
        st.metric("Crypto Fear & Greed", f"{fng['value']}/100", fng['classification'], delta_color="inverse")
        st.progress(fng['value'], text=fng['classification'])

with col2:
    btc = get_btc_price()
    if btc:
        st.metric("Bitcoin", f"${btc:,.0f}", delta=None)

with col3:
    yields = get_treasury_yields()
    if yields:
        st.metric("US 10Y Yield", f"{yields.get('10Y', 'N/A')}%")

with col4:
    stablecoins = get_stablecoins()
    if stablecoins:
        st.metric("Stablecoins", f"${stablecoins['total']:.1f}B")

st.divider()

# Row 2: Treasury Yield Curve & Economic Indicators
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 US Treasury Yield Curve")
    if yields:
        # Yield curve chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['2Y', '10Y', '30Y'],
            y=[yields.get('2Y', 0), yields.get('10Y', 0), yields.get('30Y', 0)],
            mode='lines+markers',
            name='Yield',
            line=dict(color='cyan', width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            yaxis_title='Yield (%)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Loading yield data...")

with col2:
    st.subheader("🇺🇸 US Economic Indicators")
    indicators = get_economic_indicators()
    if indicators:
        for name, value in indicators.items():
            labels = {'UNRATE': 'Unemployment', 'DFEDTARU': 'Fed Funds Rate', 'GDP': 'GDP Growth'}
            st.metric(labels.get(name, name), f"{value}%")

st.divider()

# Row 3: Stablecoins & Gold
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Stablecoin Market Cap")
    if stablecoins:
        fig = go.Figure(data=[
            go.Bar(name='Market Cap', x=['USDT', 'USDC', 'Total'], 
                   y=[stablecoins['USDT'], stablecoins['USDC'], stablecoins['total']],
                   marker_color=['green', 'blue', 'gray'])
        ])
        fig.update_layout(yaxis_title='Billion USD', template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏦 Central Bank Gold Reserves")
    gold = get_gold_reserves()
    if gold:
        fig = go.Figure(data=[
            go.Bar(name='Gold (tonnes)', x=list(gold.keys()), y=list(gold.values()),
                   marker_color='gold')
        ])
        fig.update_layout(yaxis_title='Tonnes', template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
---
**Data Sources:** FRED, CoinGecko, Coinbase, Alternative.me  
**Auto-refresh:** Every 5 minutes (Treasury Yields & Economic Indicators: 1 hour)
""")
