# ACCE v2.0 - 快速参考指南

## 🚀 快速启动
```
双击运行: C:\Users\lenovo\Desktop\启动ACCE_Web版.bat
访问地址: http://localhost:5000
```

## 📊 常用股票代码
- **美股**: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN
- **中概股**: BABA, JD, PDD, BIDU
- **A股**: 000001, 600000, 300001

## 🔧 核心配置位置

### API密钥
```
C:\Users\lenovo\Desktop\new\api assents.txt
格式: deepseek:your_key
```

### 数据源配置
```
文件: C:\Users\lenovo\TradingAgents\run_analysis_web.py
第152-177行
```

### 后端服务器
```
文件: C:\Users\lenovo\TradingAgents\web_backend.py
端口: 5000
```

### 前端界面
```
文件: C:\Users\lenovo\TradingAgents\templates\index.html
```

## 📈 K线图配置

### 图表类型
```javascript
type: 'candlestick'  // 第989行
```

### 数据格式
```javascript
{ x: '2024-03-11', o: 180, h: 185, l: 178, c: 182 }
// o:开盘, h:最高, l:最低, c:收盘
```

### 颜色方案
- 涨: #ff5252 (红)
- 跌: #00ff88 (绿)
- MA5: #ffffff (白)
- MA20: #ffff00 (黄)
- MA50: #ff9900 (橙)

## 🐛 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 图表显示错误价格 | 检查 web_backend.py 第74-77行 |
| 图表是折线不是K线 | 检查 index.html 第989行，改为 candlestick |
| WebSocket断开 | 自动重连已启用，等待3秒 |
| 编码错误 | 已修复UTF-8编码 |
| 分析报告冗余 | 已优化格式化函数 |

## 📝 修改历史

### 2026-04-09
- ✅ 实现真正的K线图（candlestick类型）
- ✅ 添加MA指标线叠加（MA5/MA20/MA50）
- ✅ 移除技术指标柱状图
- ✅ 精简分析报告格式
- ✅ 隐藏分析过程输出，只显示结果
- ✅ 修复OHLC数据传输问题
- ✅ 配置中国大陆数据源（akshare + WRDS）

## 🎯 下次更新方向
1. 十字光标拖动功能
2. 更多技术指标（RSI、MACD、布林带）
3. 加密货币支持
4. 多时间周期切换
5. 图表缩放功能
6. 导出PDF报告

---

*详细文档请查看: PROJECT_MEMORY.md*
