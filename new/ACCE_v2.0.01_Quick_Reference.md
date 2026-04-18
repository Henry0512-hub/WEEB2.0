# ACCE v2.0.01 - Quick Reference Card

## 🚀 快速启动

```
1. 双击: accev2.0.01.bat
2. 选择: 1 (DeepSeek - 推荐)
3. 输入: AAPL (股票代码)
4. 日期: 2024-06-15 到 2024-08-15
5. 等待: 自动分析完成
```

---

## ⭐ 数据源优先级

### 美股历史数据（≤ 2024-12-31）
```
1. WRDS学术数据库 ⭐ (最高准确性)
2. Alpha Vantage
3. yfinance
4. Claw爬虫
5. 模拟数据
```

### 美股实时数据（> 2024-12-31）
```
1. Alpha Vantage
2. yfinance
3. Claw爬虫
4. 模拟数据
```

---

## 📁 文件位置

```
启动器:
  C:\Users\lenovo\Desktop\accev2.0.01.bat

核心文件:
  C:\Users\lenovo\Desktop\new\

WRDS凭据:
  C:\Users\lenovo\TradingAgents\id.txt
```

---

## 🔑 API密钥

### DeepSeek
```
sk-d28ae30a58cb496c9b40e0029d0ef2c1
价格: ¥1/百万tokens
```

### Alpha Vantage
```
01D7TZIVI5LPD54Z
限制: 25次/天
```

### WRDS
```
位置: C:\Users\lenovo\TradingAgents\id.txt
格式: username=xxx, password=xxx
```

---

## 📊 常用股票代码

### 美股
```
AAPL - 苹果
TSLA - 特斯拉
NVDA - 英伟达
MSFT - 微软
GOOGL - 谷歌
AMZN - 亚马逊
```

### 中概股
```
BABA - 阿里巴巴
JD - 京东
PDD - 拼多多
BIDU - 百度
```

### 加密货币
```
BTC-USD - 比特币
ETH-USD - 以太坊
```

---

## 🧪 测试命令

```bash
# 测试WRDS连接
cd C:\Users\lenovo\Desktop\new
python test_wrds.py

# 运行主程序
python run_analysis.py
```

---

## 📝 日期格式

```
格式: YYYY-MM-DD
示例: 2024-06-15

历史数据: 2024-12-31 或之前 → 使用WRDS ⭐
实时数据: 2024-12-31 之后 → 使用Alpha Vantage
```

---

## 🎯 场景选择

| 场景 | 数据源 | 日期范围 |
|------|--------|---------|
| 学术研究 | WRDS | ≤ 2024-12-31 |
| 论文回测 | WRDS | ≤ 2024-12-31 |
| 实时分析 | Alpha Vantage | > 2024-12-31 |
| 日常使用 | yfinance | 任意日期 |
| 快速演示 | 模拟数据 | 任意日期 |

---

## ⚠️ 常见问题

### Q: WRDS连接失败？
```
1. 检查 C:\Users\lenovo\TradingAgents\id.txt 是否存在
2. 确认格式正确（username=xxx, password=xxx）
3. 尝试登录 https://wrds.wharton.upenn.edu/
```

### Q: Alpha Vantage限流？
```
系统会自动切换到yfinance，无需担心
```

### Q: 如何分析A股？
```
当前版本正在开发中，请使用中概股代码（BABA、JD）
```

---

## 📞 获取帮助

```
文档: C:\Users\lenovo\Desktop\new\README.md
发布说明: C:\Users\lenovo\Desktop\ACCE_v2.0.01_RELEASE.md
WRDS指南: C:\Users\lenovo\TradingAgents\WRDS_PRIORITY_GUIDE.md
```

---

## 🔄 版本升级

```
当前版本: v2.0.01
下一版本: v2.0.02 (规划中)

升级方式:
  1. 复制 new 目录到 new_v2.0.02
  2. 修改核心文件
  3. 创建新启动器 accev2.0.02.bat
```

---

**ACCE v2.0.01 - Quick Reference**

*更新时间: 2026-04-09*
