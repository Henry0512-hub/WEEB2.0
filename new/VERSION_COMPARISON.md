# 重要说明 - 两个版本对比

## 🎯 两个启动器

### 1. acce_v2.0.01_Full.bat ⭐⭐⭐ 推荐

**位置**: `C:\Users\lenovo\Desktop\acce_v2.0.01_Full.bat`

**功能**: 完整的TradingAgents系统

**包含**:
- ✅ 8个AI智能体协同工作
- ✅ 技术面分析（Technical Analysis）
- ✅ 基本面分析（Fundamental Analysis）
- ✅ 情绪面分析（Sentiment Analysis）
- ✅ 新闻分析（News Analysis）
- ✅ 投资建议和风险评估
- ✅ 完整的TradingAgents框架

**使用方法**:
```bash
# 双击运行
acce_v2.0.01_Full.bat

# 或命令行
cd C:\Users\lenovo\TradingAgents
python run_enhanced_analysis.py AAPL 2022-03-02 2022-03-18 1 1
```

**参数说明**:
```
参数1: 股票代码（AAPL）
参数2: 开始日期（2022-03-02）
参数3: 结束日期（2022-03-18）
参数4: 分析师（1=DeepSeek, 2=Kimi, 3=Gemini）
参数5: 分析类型（1=完整, 2=快速, 3=情绪）
```

---

### 2. accev2.0.01.bat ⚠️ 简化版

**位置**: `C:\Users\lenovo\Desktop\accev2.0.01.bat`

**功能**: 简化的数据获取系统

**包含**:
- ⚠️ 仅数据获取
- ⚠️ 无AI分析
- ⚠️ 无智能体协同
- ⚠️ 无投资建议

**不推荐使用！**

---

## ⚡ 快速开始

### 推荐：使用完整版

```bash
# 1. 双击启动器
acce_v2.0.01_Full.bat

# 2. 选择分析师
输入: 1 (DeepSeek - 推荐)

# 3. 输入股票代码
输入: AAPL

# 4. 输入日期范围
开始: 2022-03-02
结束: 2022-03-18

# 5. 选择分析类型
输入: 1 (完整分析)

# 6. 等待完整分析
- 8个AI智能体协同工作
- 技术、基本面、情绪分析
- 最终投资建议
```

---

## 📊 功能对比

| 功能 | Full版 | 简化版 |
|------|--------|--------|
| 数据获取 | ✅ | ✅ |
| WRDS优先级 | ✅ | ✅ |
| 8个AI智能体 | ✅ | ❌ |
| 技术分析 | ✅ | ❌ |
| 基本面分析 | ✅ | ❌ |
| 情绪分析 | ✅ | ❌ |
| 新闻分析 | ✅ | ❌ |
| 投资建议 | ✅ | ❌ |
| 完整框架 | ✅ | ❌ |

---

## 🔧 为什么有两个版本？

**历史原因**:
1. 最初创建了简化版（功能缺失）
2. 发现原系统有完整功能
3. 创建了Full版（推荐使用）

**建议**:
- ✅ 使用 `acce_v2.0.01_Full.bat`
- ❌ 不要使用 `accev2.0.01.bat`

---

## 🚀 完整版使用示例

### 分析苹果公司

```bash
# 启动
acce_v2.0.01_Full.bat

# 输入
分析师: 1 (DeepSeek)
股票: AAPL
开始: 2022-03-02
结束: 2022-03-18
类型: 1 (完整)

# 输出
[智能体协同]
- 市场分析师: 分析价格趋势
- 社交媒体分析师: 分析社区情绪
- 新闻分析师: 分析行业新闻
- 基本面分析师: 分析财务数据
- 牛市研究员: 多头论证
- 熊市研究员: 空头论证
- 交易员: 制定策略
- 投资组合经理: 最终评级

[最终建议]
推荐: 买入/持有/卖出
理由: 详细分析
风险: 风险提示
```

---

## 📁 工作目录

### Full版
```
C:\Users\lenovo\TradingAgents\
├── run_enhanced_analysis.py        # 主程序
├── run_with_deepseek.py            # DeepSeek版
├── run_with_kimi.py                # Kimi版
├── run_with_gemini.py              # Gemini版
├── run_news_analysis.py            # 新闻分析
├── run_crypto_trading.py           # 加密货币
└── tradingagents/                  # 核心框架
```

### 简化版
```
C:\Users\lenovo\Desktop\new\
├── intelligent_data_fetcher.py     # 数据获取
├── run_analysis.py                 # 简化分析
└── (无完整框架)
```

---

## ✅ 正确的使用方式

### 日常使用

```bash
# 使用完整版
acce_v2.0.01_Full.bat

# 原TradingAgents目录
cd C:\Users\lenovo\TradingAgents
python run_enhanced_analysis.py AAPL 2022-03-02 2022-03-18 1 1
```

### 其他功能

```bash
# 新闻分析
cd C:\Users\lenovo\TradingAgents
python run_news_analysis.py

# 加密货币
python run_crypto_trading.py

# WRDS深度分析
python run_wrds_deepseek.py
```

---

## 🎓 总结

**你应该使用**:
- ✅ `acce_v2.0.01_Full.bat` - 完整功能
- ✅ 原TradingAgents目录 - 所有功能

**不要使用**:
- ❌ `accev2.0.01.bat` - 功能缺失
- ❌ `C:\Users\lenovo\Desktop\new\` - 简化版

---

**推荐：使用完整版，享受所有功能！** 🚀

---

*更新时间: 2026-04-09*
*版本: Full v2.0.01*
