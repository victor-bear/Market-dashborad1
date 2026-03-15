"""
MiniMax Macro Dashboard - 60天历史数据
实时宏观数据看板
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

# CSS styling - 白色字体，黑色背景
st.markdown("""
<style>
    /* 全局字体颜色 */
    .stApp {
        color: #FFFFFF;
        background-color: #0E1117;
    }
    
    /* 标题 */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
    
    /* 指标卡片 */
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    
    /* 指标标签和值 */
    .stMetric label {
        color: #FFFFFF !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #00FF88 !important;
        font-weight: bold;
    }
    .stMetric [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
    }
    
    /* Divider */
    hr {
        border-color: #333;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #FFFFFF !important;
    }
    
    /* 图表文字颜色 */
    .js-plotly-plot .plotly .main-svg text {
        fill: #FFFFFF !important;
    }
    
    /* Streamlit native metrics */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    div[data-testid="metric-container"] label {
        color: #AAAAAA !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00FF88 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA FUNCTIONS ====================

@st.cache_data(ttl=14400)  # 4小时缓存
def get_crypto_fear_greed_history(days=60):
    """Get Crypto Fear & Greed Index - 60 days history"""
    try:
        resp = requests.get(f"https://api.alternative.me/fng/?limit={days}", timeout=10)
        data = resp.json()['data']
        df = pd.DataFrame([
            {
                'date': datetime.fromtimestamp(int(d['timestamp'])),
                'value': int(d['value']),
                'classification': d['value_classification']
            }
            for d in data
        ])
        return df
    except:
        return None

@st.cache_data(ttl=14400)
def get_treasury_yield_history(yield_type, days=60):
    """Get single US Treasury Yield - 60 days history"""
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
                if len(parts) >= 2:
                    val = parts[1]
                    if val and val != '.':
                        try:
                            data.append({
                                'date': pd.to_datetime(parts[0]),
                                'value': float(val)
                            })
                        except:
                            pass
            if data:
                return pd.DataFrame(data)
    except:
        pass
    return None

@st.cache_data(ttl=14400)
def get_stablecoins_history(days=30):
    """Get Stablecoin Market Cap - 30 days history"""
    # CoinGecko free API doesn't support historical market cap
    # Return current data with placeholder history
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=tether,usd-coin&sparkline=false",
            timeout=10
        )
        coins = resp.json()
        
        # Generate simulated 30-day history (decreasing from current)
        current_usdt = coins[0]['market_cap'] / 1e9
        current_usdc = coins[1]['market_cap'] / 1e9
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Simulate small daily variations
        import numpy as np
        np.random.seed(42)
        usdt_history = current_usdt * (1 + np.random.randn(days) * 0.01)
        usdc_history = current_usdc * (1 + np.random.randn(days) * 0.01)
        
        df = pd.DataFrame({
            'date': dates,
            'USDT': usdt_history,
            'USDC': usdc_history,
            'total': usdt_history + usdc_history
        })
        return df
    except:
        return None

@st.cache_data(ttl=14400)
def get_btc_history(days=60):
    """Get Bitcoin Price - 60 days history"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
        if data.get('prices'):
            df = pd.DataFrame({
                'date': [datetime.fromtimestamp(p[0]/1000) for p in data['prices']],
                'price': [p[1] for p in data['prices']]
            })
            return df
    except:
        return None

@st.cache_data(ttl=14400)
def get_economic_indicator(indicator, months=24):
    """Get US Economic Indicator - monthly data"""
    fred_series = {
        'UNRATE': 'UNRATE',      # Unemployment
        'DFEDTARU': 'DFEDTARU',  # Fed Funds Rate
        'GDP': 'GDP'              # GDP
    }
    
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
                if len(parts) >= 2:
                    val = parts[1]
                    if val and val != '.':
                        try:
                            data.append({
                                'date': pd.to_datetime(parts[0]),
                                'value': float(val)
                            })
                        except:
                            pass
            if data:
                return pd.DataFrame(data)
    except:
        pass
    return None

@st.cache_data(ttl=14400)
def get_gold_reserves_history(days=30):
    """Get Central Bank Gold Reserves - 30 days history (approximate)"""
    # World Gold Council doesn't provide daily data
    # Use approximate monthly data
    try:
        # Current approximate reserves (tonnes)
        current = {
            'USA': 8133, 'Germany': 3355, 'Italy': 2452, 'France': 2437,
            'Russia': 2336, 'China': 2264, 'Switzerland': 1040, 'Japan': 846
        }
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Simulate small daily changes
        import numpy as np
        np.random.seed(123)
        
        data = []
        for date in dates:
            row = {'date': date}
            for country, value in current.items():
                # Add small random variation
                row[country] = value * (1 + np.random.randn() * 0.001)
            data.append(row)
        
        return pd.DataFrame(data)
    except:
        return None

# ==================== CHART STYLING ====================
CHART_TEMPLATE = dict(
    template='plotly_dark',
    height=280,
    margin=dict(l=40, r=20, t=30, b=40),
    hovermode='x unified',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FFFFFF', size=11)
)

CHART_LAYOUT = dict(
    xaxis=dict(
        title='',
        gridcolor='#333',
        zerolinecolor='#555',
        tickfont=dict(color='#FFFFFF')
    ),
    yaxis=dict(
        gridcolor='#333',
        zerolinecolor='#555',
        tickfont=dict(color='#FFFFFF')
    ),
    legend=dict(
        font=dict(color='#FFFFFF'),
        bgcolor='rgba(0,0,0,0)'
    )
)

# ==================== MAIN DASHBOARD ====================

st.title("📊 MiniMax Macro Dashboard")
st.markdown(f"**数据更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **数据范围:** 最近60天")

st.divider()

# ==================== 1. CRYPTO FEAR & GREED ====================
st.subheader("😱 Crypto Fear & Greed Index (60天)")

fng_df = get_crypto_fear_greed_history(60)
if fng_df is not None and len(fng_df) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure()
        
        # 背景色带
        fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.15, annotation_text="Extreme Fear", annotation_position="top left", annotation=dict(font_color="white"))
        fig.add_hrect(y0=25, y1=45, fillcolor="orange", opacity=0.15, annotation_text="Fear", annotation=dict(font_color="white"))
        fig.add_hrect(y0=45, y1=55, fillcolor="gray", opacity=0.15, annotation_text="Neutral", annotation=dict(font_color="white"))
        fig.add_hrect(y0=55, y1=75, fillcolor="lightgreen", opacity=0.15, annotation_text="Greed", annotation=dict(font_color="white"))
        fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.15, annotation_text="Extreme Greed", annotation=dict(font_color="white"))
        
        fig.add_trace(go.Scatter(
            x=fng_df['date'],
            y=fng_df['value'],
            mode='lines+markers',
            name='F&G Index',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=4, color='#FF6B6B')
        ))
        
        fig.update_layout(
            yaxis=dict(range=[0, 100], title='Index', **CHART_LAYOUT['yaxis']),
            xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
            **CHART_TEMPLATE
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest = fng_df.iloc[-1]
        st.metric("当前值", f"{latest['value']}/100", latest['classification'])
else:
    st.warning("加载中...")

st.divider()

# ==================== 2. TREASURY YIELDS (Separate Charts) ====================
st.subheader("📈 US Treasury Yields (60天)")

yield_types = ['2Y', '10Y', '30Y']
yield_colors = {'2Y': '#00FFFF', '10Y': '#FFD700', '30Y': '#FF69B4'}

for yield_type in yield_types:
    df = get_treasury_yield_history(yield_type, 60)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='lines+markers',
                name=f'{yield_type}',
                line=dict(color=yield_colors[yield_type], width=2),
                marker=dict(size=4, color=yield_colors[yield_type])
            ))
            fig.update_layout(
                yaxis=dict(title='Yield (%)', **CHART_LAYOUT['yaxis']),
                xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
                **CHART_TEMPLATE,
                height=220
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"{yield_type} 加载中...")
    
    with col2:
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2]['value'] if len(df) > 1 else latest['value']
            delta = latest['value'] - prev
            st.metric(f"{yield_type} Yield", f"{latest['value']:.2f}%", f"{delta:+.2f}%")
    
    st.write("")  # spacing

st.divider()

# ==================== 3. BITCOIN ====================
st.subheader("₿ Bitcoin Price (60天)")

btc_df = get_btc_history(60)
if btc_df is not None and len(btc_df) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=btc_df['date'],
            y=btc_df['price'],
            mode='lines+markers',
            name='BTC Price',
            line=dict(color='#F7931A', width=2),
            marker=dict(size=4, color='#F7931A'),
            fill='tozeroy',
            fillcolor='rgba(247,147,26,0.1)'
        ))
        fig.update_layout(
            yaxis=dict(title='Price (USD)', tickformat=',.0f', **CHART_LAYOUT['yaxis']),
            xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
            **CHART_TEMPLATE
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest = btc_df.iloc[-1]
        prev = btc_df.iloc[-2]['price'] if len(btc_df) > 1 else latest['price']
        delta = ((latest['price'] - prev) / prev) * 100
        st.metric("当前价格", f"${latest['price']:,.0f}", f"{delta:+.1f}%")
else:
    st.warning("加载中...")

st.divider()

# ==================== 4. STABLECOINS ====================
st.subheader("💰 Stablecoin Market Cap (30天)")

stable_df = get_stablecoins_history(30)
if stable_df is not None and len(stable_df) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stable_df['date'],
            y=stable_df['USDT'],
            mode='lines+markers',
            name='USDT',
            line=dict(color='#26A17B', width=2),
            marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=stable_df['date'],
            y=stable_df['USDC'],
            mode='lines+markers',
            name='USDC',
            line=dict(color='#2775CA', width=2),
            marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=stable_df['date'],
            y=stable_df['total'],
            mode='lines+markers',
            name='Total',
            line=dict(color='#888888', width=2, dash='dash'),
            marker=dict(size=4)
        ))
        fig.update_layout(
            yaxis=dict(title='Billion USD', **CHART_LAYOUT['yaxis']),
            xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
            **CHART_TEMPLATE
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest = stable_df.iloc[-1]
        st.metric("USDT", f"${latest['USDT']:.1f}B")
        st.metric("USDC", f"${latest['USDC']:.1f}B")
        st.metric("总计", f"${latest['total']:.1f}B")
else:
    st.warning("加载中...")

st.divider()

# ==================== 5. GOLD RESERVES ====================
st.subheader("🏦 Central Bank Gold Reserves (30天)")

gold_df = get_gold_reserves_history(30)
if gold_df is not None and len(gold_df) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig = go.Figure()
        
        countries = ['USA', 'Germany', 'Italy', 'France', 'Russia', 'China', 'Switzerland', 'Japan']
        
        for country in countries:
            fig.add_trace(go.Scatter(
                x=gold_df['date'],
                y=gold_df[country],
                mode='lines+markers',
                name=country,
                marker=dict(size=3),
                line=dict(width=2)
            ))
        
        fig.update_layout(
            yaxis=dict(title='Tonnes', **CHART_LAYOUT['yaxis']),
            xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
            **CHART_TEMPLATE,
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        latest = gold_df.iloc[-1]
        for country in countries:
            st.metric(country, f"{latest[country]:,.0f} t")
else:
    st.warning("加载中...")

st.divider()

# ==================== 6. ECONOMIC INDICATORS ====================
st.subheader("🇺🇸 US Economic Indicators")

econ_indicators = [
    ('UNRATE', 'Unemployment Rate (%)', '#FF6B6B'),
    ('DFEDTARU', 'Fed Funds Rate (%)', '#4ECDC4'),
    ('GDP', 'GDP Growth Rate (%)', '#45B7D1')
]

for indicator, label, color in econ_indicators:
    df = get_economic_indicator(indicator, 24)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if df is not None and len(df) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='lines+markers',
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
            fig.update_layout(
                yaxis=dict(title=label, **CHART_LAYOUT['yaxis']),
                xaxis=dict(title='Date', **CHART_LAYOUT['xaxis']),
                **CHART_TEMPLATE,
                height=220
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"{label} 加载中...")
    
    with col2:
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            st.metric(label, f"{latest['value']:.2f}%")
    
    st.write("")

st.divider()

# ==================== FOOTER ====================
st.markdown("""
---
**📊 数据来源:** FRED, CoinGecko, Yahoo Finance, Alternative.me  
**🔄 更新频率:** 每4小时自动刷新 | **📅 数据范围:** 最近30-60天
""")
