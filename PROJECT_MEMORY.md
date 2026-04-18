# ACCE v2.0 - 项目记忆文件

## 📋 项目概述

**项目名称**: ACCE v2.0 (AI Crypto & Currency Exchange)
**版本**: v2.0 Web
**创建时间**: 2026-04-09
**项目路径**: `C:\Users\lenovo\TradingAgents`

### 核心功能
- 基于 TradingAgents 框架的智能交易分析系统
- 8个AI智能体协同工作（市场分析师、社交媒体分析师、新闻分析师、基本面分析师、牛市研究员、熊市研究员、交易员、投资组合经理）
- Web界面：后现代主义霓虹风格，实时K线图展示
- 支持美股、A股、加密货币（加密货币功能暂未上线）

---

## 🛠️ 技术栈

### 后端
- **框架**: Flask + Flask-Sock (WebSocket)
- **Python版本**: 3.13
- **核心引擎**: TradingAgents (8个AI智能体)
- **数据源**:
  - 美股 (≤2024-12-31): WRDS 学术数据库
  - 美股 (>2024-12-31): akshare
  - A股: akshare
  - 加密货币: 暂未上线

### 前端
- **HTML5** + **CSS3** + **JavaScript**
- **图表库**: Chart.js + chartjs-chart-financial (K线图)
- **时间处理**: Luxon + chartjs-adapter-luxon
- **实时通信**: WebSocket (Flask-Sock)
- **设计风格**: 后现代主义霓虹风格（青色 #00ffff、洋红色 #ff00ff）

### LLM支持
- **DeepSeek** (推荐) - ¥1/百万tokens
- **Kimi** - 中文优化，128k上下文
- **Gemini** - 免费，每天1500次请求

---

## 📁 文件结构

```
C:\Users\lenovo\TradingAgents\
├── web_backend.py              ⭐ Flask后端服务器
├── run_analysis_web.py         ⭐ 支持命令行参数的分析脚本
├── templates/
│   └── index.html              ⭐ 前端HTML界面（K线图）
├── 【桌面启动器】
│   └── 启动ACCE_Web版.bat      ⭐ 一键启动器
├── 【API密钥配置】
│   └── api assents.txt          ⭐ LLM API密钥文件
│   └── av api.txt              ⭐ Alpha Vantage API
│   └── id.txt                  ⭐ WRDS凭据
└── tradingagents/              ⭐ TradingAgents框架
```

---

## 🔑 关键配置文件

### 1. API密钥文件
**路径**: `C:\Users\lenovo\Desktop\new\api assents.txt`

**格式**:
```
deepseek:your_api_key
kimi:your_api_key
gemini:your_api_key
```

### 2. 数据源配置
**文件**: `run_analysis_web.py` (第152-177行)

```python
if market_type == 'cn':
    # A股使用 akshare
    trade_config["data_vendors"] = {"core_stock_apis": "akshare"}
elif market_type == 'crypto':
    # 加密货币暂不支持
    print("[错误] 加密货币功能暂未上线")
    return
else:
    # 美股根据日期选择数据源
    if start_dt <= cutoff_dt:
        # 使用 WRDS 学术数据库
        trade_config["data_vendors"] = {"core_stock_apis": "wrds"}
    else:
        # 使用 akshare
        trade_config["data_vendors"] = {"core_stock_apis": "akshare"}
```

---

## 📊 前端图表实现

### K线图配置
**文件**: `templates/index.html` (第984-1125行)

**图表类型**: `candlestick`

**数据格式**:
```javascript
candlestickData = [
    { x: '2024-03-11', o: 180, h: 185, l: 178, c: 182 },
    // o: 开盘价, h: 最高价, l: 最低价, c: 收盘价
]

indicatorLines = {
    ma5: [{ x: '2024-03-11', y: 180.5 }],
    ma20: [{ x: '2024-03-11', y: 178.2 }],
    ma50: [{ x: '2024-03-11', y: 175.8 }]
}
```

**颜色方案**:
- 涨: 红色 `#ff5252`
- 跌: 绿色 `#00ff88`
- MA5: 白色 `#ffffff`
- MA20: 黄色 `#ffff00`
- MA50: 橙色 `#ff9900`

### WebSocket数据解析
**文件**: `templates/index.html` (第750-809行)

```javascript
// 解析OHLC数据（CSV格式：Date,Open,High,Low,Close,Volume）
const ohlcMatch = text.match(/^(\d{4}-\d{2}-\d{2}),([\d.]+),([\d.]+),([\d.]+),([\d.]+),/);
if (ohlcMatch) {
    candlestickData.push({
        x: ohlcMatch[1],  // 日期
        o: parseFloat(ohlcMatch[2]),  // 开盘
        h: parseFloat(ohlcMatch[3]),  // 最高
        l: parseFloat(ohlcMatch[4]),  // 最低
        c: parseFloat(ohlcMatch[5])   // 收盘
    });
    updateChart();
}

// 解析MA指标
const ma20Match = text.match(/MA20[=：\s]*([\d.]+)/i);
const ma50Match = text.match(/MA50[=：\s]*([\d.]+)/i);
```

---

## 🔧 后端数据处理

### OHLC数据不过滤
**文件**: `web_backend.py` (第64-140行)

**关键修改**: CSV OHLC数据必须发送到前端用于绘图

```python
def parse_trading_output(text):
    # 检测是否是CSV OHLC数据行
    csv_ohlc_pattern = r'^\d{4}-\d{2}-\d{2},[\d.]+,[\d.]+,[\d.]+,[\d.]+,[\d.]+,'
    if re.match(csv_ohlc_pattern, text.strip()):
        stage = 'price_data'  # 标记为价格数据，不过滤

    # OHLC数据不跳过，其他数据按原规则过滤
    if stage != 'price_data':
        for pattern in skip_patterns:
            if pattern in text:
                return None
```

### 数据过滤规则
**跳过的内容**:
- JSON财务数据字段
- Tool Calls/Function/Response
- 技术指标描述
- FutureWarning/Deprecated警告
- yfinance相关数据（已移除）

**保留的内容**:
- 所有 `[XXX]` 格式的消息
- 智能体输出（市场分析师、新闻分析师等）
- 投资建议（推荐：买入/卖出/持有）
- CSV OHLC价格数据
- MA指标数据

---

## 🚀 启动方式

### 方法1：使用桌面启动器（推荐）
```
双击运行: C:\Users\lenovo\Desktop\启动ACCE_Web版.bat
```

### 方法2：手动启动
```bash
cd C:\Users\lenovo\TradingAgents
python -m pip install flask flask-sock flask-cors
python web_backend.py
```

### 访问地址
```
http://localhost:5000
http://127.0.0.1:5000
http://192.168.92.101:5000  (局域网访问)
```

---

## 🎨 界面设计

### 后现代主义霓虹风格
**主色调**:
- 霓虹青: `#00ffff`
- 霓虹洋红: `#ff00ff`
- 霓虹黄: `#ffff00`
- 霓虹绿: `#00ff00`
- 深色背景: `#0a0e27`

**特效**:
- 动态渐变背景
- 网格叠加层
- 毛玻璃效果 (backdrop-filter: blur)
- 霓虹灯发光效果
- 流畅的过渡动画

### 布局结构
1. **控制面板** - 选择分析师、输入股票代码、选择日期
2. **工作流程图** - 8个AI智能体节点，霓虹灯效果
3. **K线图** - 真实OHLC数据 + MA指标线叠加
4. **分析报告** - 精简格式，按智能体分组
5. **相关新闻** - 情绪分析
6. **终端输出** - 简洁日志，分析完成后自动清空

---

## 📝 常用股票代码

### 美股
- `AAPL` - 苹果
- `TSLA` - 特斯拉
- `NVDA` - 英伟达
- `MSFT` - 微软
- `GOOGL` - 谷歌
- `AMZN` - 亚马逊

### 中概股
- `BABA` - 阿里巴巴
- `JD` - 京东
- `PDD` - 拼多多
- `BIDU` - 百度

### A股
- `000001` - 平安银行
- `600000` - 浦发银行
- `300001` - 特锐德

---

## ⚠️ 注意事项

### 1. 日期选择
- 开始日期 ≤ 2024-12-31：使用WRDS学术数据库
- 开始日期 > 2024-12-31：使用实时数据（akshare）

### 2. 分析时间
- 完整分析：约5-10分钟
- 快速分析：约3-5分钟
- 情绪分析：约2-3分钟

### 3. 浏览器兼容性
- 推荐使用 Chrome、Edge、Firefox
- 需要支持 WebSocket
- 需要支持 JavaScript

### 4. 中国大陆用户
- ✅ A股: 使用 akshare（国内可用）
- ✅ 美股(≤2024-12-31): 使用 WRDS（学术数据库）
- ✅ 美股(>2024-12-31): 使用 akshare
- ❌ 加密货币: 暂未上线
- ❌ yfinance: 已移除（有网络限制）

---

## 🔍 常见问题解决

### 问题1: 图表显示错误的价格范围
**原因**: OHLC数据被后端过滤掉了
**解决**: 检查 `web_backend.py` 第74-77行，确保CSV数据不过滤

### 问题2: 图表类型显示为折线而非K线
**原因**: 图表类型未改为 'candlestick'
**解决**: 检查 `templates/index.html` 第989行，应该是 `type: 'candlestick'`

### 问题3: 编码错误（emoji显示为方框）
**原因**: Windows GBK编码问题
**解决**: 已在 `run_analysis_web.py` 添加UTF-8编码包装

### 问题4: WebSocket连接断开
**原因**: 网络波动或服务重启
**解决**: 前端已实现自动重连机制（最多5次，间隔3秒）

### 问题5: 分析报告显示无意义内容
**解决**: 已优化 `formatAnalysisReport()` 函数，只保留关键信息

---

## 📦 依赖安装

### Python依赖
```bash
pip install flask flask-sock flask-cors
pip install tradingagents
pip install python-dotenv
```

### 前端CDN（自动加载）
- Chart.js
- chartjs-chart-financial
- Luxon
- chartjs-adapter-luxon

---

## 🎯 后续更新方向

1. **十字光标拖动功能** - 实现真正的可拖动十字线
2. **更多技术指标** - RSI、MACD、布林带等
3. **加密货币支持** - 接入实时加密货币数据
4. **多时间周期** - 日线、周线、月线切换
5. **图表缩放** - 支持放大/缩小查看细节
6. **导出功能** - 导出分析报告为PDF

---

## 📞 技术支持

**项目路径**: `C:\Users\lenovo\TradingAgents`
**启动器**: `C:\Users\lenovo\Desktop\启动ACCE_Web版.bat`
**访问地址**: http://localhost:5000

---

*最后更新: 2026-04-09*
*状态: 生产环境运行中*
