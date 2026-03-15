# 📊 MiniMax Macro Dashboard

实时宏观数据看板 (Streamlit Web App)

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py
```

访问 http://localhost:8501

---

## 🌐 部署到云端

### 方法1: Streamlit Cloud (免费)

1. 上传代码到 GitHub
2. 访问 https://streamlit.io/cloud
3. 连接 GitHub 仓库
4. 部署！

### 方法2: Railway / Render (免费)

```bash
# railway.app
railway init
railbox deploy
```

### 方法3: Docker 部署

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 📱 手机访问

部署后用手机浏览器打开同样可以查看，自动适配移动端。

---

## ⚙️ 功能

- [x] Crypto Fear & Greed Index
- [x] US Treasury Yields (2Y, 10Y, 30Y)
- [x] Bitcoin Price
- [x] Stablecoin Market Cap (USDT, USDC)
- [x] US Economic Indicators (Unemployment, Fed Rate, GDP)
- [x] Central Bank Gold Reserves
- [x] Auto-refresh (5分钟/1小时)
- [x] Dark Mode
- [x] Mobile Responsive

---

## 🔧 自定义

修改 `app.py` 中的 `@st.cache_data(ttl=秒数)` 调整缓存时间。

## 📝 待添加

- DXY 美元指数
- BTC ETF Flows
- 各国央行黄金季度购买
- 更多经济指标 (CPI, PMI等)
