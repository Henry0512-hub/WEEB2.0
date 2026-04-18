# TradingAgents 快速指南

## 🎯 立即开始

### 双击桌面上的 **TradingAgents启动器.bat**

---

## 📊 三个已配置的 LLM API

| API | 价格 | 特点 | 推荐场景 |
|-----|------|------|----------|
| **DeepSeek** | ¥1/百万tokens | 最便宜, 稳定, 中文好 | ⭐ 日常使用 |
| **Kimi** | 付费 | 中文最强, 128k上下文 | 中文任务 |
| **Gemini** | 免费1500次/天 | 推理强 | 测试学习 |

---

## 🚀 快速命令

```bash
# 进入目录
cd C:\Users\lenovo\TradingAgents

# 使用 DeepSeek (推荐)
python run_with_deepseek.py

# 使用 Kimi (中文最好)
python run_with_kimi.py

# 使用 Gemini (免费)
python run_with_gemini.py

# 交互式模式
python run_with_deepseek_interactive.py

# 加密货币分析
python run_crypto_trading.py

# 新闻分析
python run_news_analysis.py
```

---

## 📁 项目位置

**主目录**: `C:\Users\lenovo\TradingAgents\`

**启动器**: `C:\Users\lenovo\Desktop\TradingAgents启动器.bat`

---

## 🔑 API 密钥

### DeepSeek
```
Key: sk-d28ae30a58cb496c9b40e0029d0ef2c1
URL: https://api.deepseek.com
```

### Kimi
```
Key: sk-PBksAJzkTW48yH12moqKci3hckekib80qJzMz63MG4XVfPyd
URL: https://api.moonshot.cn
```

### Gemini
```
Key: AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk
URL: https://ai.google.dev
```

---

## ✅ 系统已包含

- ✅ TradingAgents 框架 (v0.2.3)
- ✅ 3个 LLM API 已配置
- ✅ 美股数据源 (yfinance)
- ✅ 中国数据源 (akshare)
- ✅ 宏观数据 (fredapi)
- ✅ WRDS 支持
- ✅ 加密货币支持
- ✅ 新闻分析功能

---

## 📚 文档位置

在 `C:\Users\lenovo\TradingAgents\` 目录下:

- `使用指南.md` - 基础使用
- `所有API配置总结.md` - API详细配置
- `API_CONFIG_GUIDE.md` - 英文配置指南
- `QUICK_START.md` - 快速开始
- `TROUBLESHOOTING.md` - 故障排除

---

## 🎓 推荐使用流程

### 1. 测试环境
打开启动器 → 选择 "11. 系统环境检查"

### 2. 测试 API
打开启动器 → 选择 "8/9/10. 测试 API"

### 3. 第一次分析
打开启动器 → 选择 "1. DeepSeek API"
输入股票代码: AAPL

### 4. 尝试不同股票
- 美股: AAPL, TSLA, NVDA, MSFT
- 中概股: BABA, JD, PDD
- 加密货币: BTC, ETH

---

## 💡 使用技巧

### 降低成本
```python
# 减少辩论轮数
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
```

### 提高质量
```python
# 增加辩论轮数
config["max_debate_rounds"] = 2
```

### 中文输出
```python
config["output_language"] = "Chinese"
```

---

## 🔧 常见问题

### Q: 哪个 API 最便宜？
A: DeepSeek，¥1/百万 tokens

### Q: 哪个 API 中文最好？
A: Kimi，专为中文优化

### Q: 哪个 API 免费？
A: Gemini，每天1500次免费

### Q: 如何分析中国 A 股？
A: 使用 akshare 数据源，系统已集成

### Q: 如何分析加密货币？
A: 使用启动器选项 6，或运行 `python run_crypto_trading.py`

---

## 📞 获取帮助

1. 查看 `使用指南.md`
2. 查看 `TROUBLESHOOTING.md`
3. 运行测试脚本验证环境

---

**开始使用: 双击桌面上的 `TradingAgents启动器.bat`**

**祝你分析愉快！🚀**
