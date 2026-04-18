# ACCE v2.0.01 - 快速启动指南 ⚡

## 🚀 5分钟快速开始

### 步骤1：检查API密钥文件（1分钟）

**三个必需的文件**：

```bash
# 1. WRDS凭据
位置: C:\Users\lenovo\TradingAgents\id.txt
内容:
username: hengyang24
password: Appleoppo17@

# 2. Alpha Vantage API
位置: C:\Users\lenovo\TradingAgents\av api.txt
内容:
01D7TZIVI5LPD54Z

# 3. LLM APIs
位置: C:\Users\lenovo\Desktop\new\api assents.txt
内容:
deepseek: sk-aa0ac23b61974015826717b2ba86dec3
kimi: sk-zuVM5fhu24KzBytPVhcz8lF6k37GNqXnZcQRAwgfj3GBeN53
gemini: AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk
```

**检查方法**：
```bash
# 确认文件存在
dir "C:\Users\lenovo\TradingAgents\id.txt"
dir "C:\Users\lenovo\TradingAgents\av api.txt"
dir "C:\Users\lenovo\Desktop\new\api assents.txt"
```

---

### 步骤2：测试API配置（1分钟）

```bash
cd C:\Users\lenovo\Desktop\new
python test_all_apis.py
```

**期望看到**：
```
[PASS] WRDS
[PASS] Alpha Vantage
[PASS] LLM APIs
[SUCCESS] All API keys are configured correctly!
```

---

### 步骤3：启动系统（2分钟）

**方法1：双击启动器**
```
双击桌面上的：accev2.0.01.bat
```

**方法2：命令行**
```bash
cd C:\Users\lenovo\Desktop\new
python run_analysis.py
```

---

### 步骤4：分析股票（1分钟）

**示例：分析苹果公司历史数据**

```
1. 选择分析师
   输入: 1
   说明: DeepSeek（最便宜）

2. 输入股票代码
   输入: AAPL
   说明: 苹果公司

3. 输入开始日期
   输入: 2022-03-12
   说明: 2022年3月12日（会自动使用WRDS ⭐）

4. 输入结束日期
   输入: 2023-04-12
   说明: 2023年4月12日

5. 等待分析完成
   时间: 约30秒-2分钟
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

## 🎯 数据源自动选择

### 规则很简单

```
如果日期 ≤ 2024-12-31:
    使用WRDS ⭐（最准确）

如果日期 > 2024-12-31:
    使用Alpha Vantage（实时数据）
```

### 示例

| 股票 | 日期范围 | 数据源 |
|------|---------|--------|
| AAPL | 2022-01-01 到 2022-12-31 | WRDS ⭐ |
| TSLA | 2023-06-01 到 2023-12-31 | WRDS ⭐ |
| NVDA | 2024-01-01 到 2024-06-30 | WRDS ⭐ |
| AAPL | 2025-01-01 到 2025-04-09 | Alpha Vantage |
| TSLA | 2025-03-01 到 今天 | Alpha Vantage |

---

## 🔑 API密钥获取

### 如果缺少API密钥

#### WRDS（学术数据库）
```
1. 访问: https://wrds.wharton.upenn.edu/
2. 用学术邮箱注册
3. 等待1-2天
4. 保存到: C:\Users\lenovo\TradingAgents\id.txt
```

#### Alpha Vantage
```
1. 访问: https://www.alphavantage.co/support/#api-key
2. 免费注册
3. 立即获取
4. 保存到: C:\Users\lenovo\TradingAgents\av api.txt
```

#### DeepSeek（推荐）
```
1. 访问: https://platform.deepseek.com/
2. 注册账号
3. 获取API密钥
4. 保存到: C:\Users\lenovo\Desktop\new\api assents.txt
```

---

## ⚡ 快速测试命令

### 测试所有API
```bash
cd C:\Users\lenovo\Desktop\new
python test_all_apis.py
```

### 测试WRDS连接
```bash
python test_wrds.py
```

### 测试完整系统
```bash
python test_system.py
```

---

## 🎨 系统输出示例

### 成功的分析

```
[Loading] Loading LLM API keys...
[OK] Loaded 3 LLM API key(s)
     - DEEPSEEK: sk-aa0ac2...
     - KIMI: sk-zuVM5f...
     - GEMINI: AIzaSyA...

[Priority Strategy] Detected US stock historical data
[Try 1/5] *** Using WRDS Academic Database...
[WRDS] Connecting to WRDS database as hengyang24...
[WRDS] Fetching AAPL data from CRSP...
[WRDS] Successfully fetched 283 records
[Success] Got 283 records from WRDS ***

[Data Summary]
Data Source: WRDS Academic Database
Ticker: AAPL
Date Range: 2022-03-12 to 2023-04-12
Records: 283
Latest Price: $178.99
Price Range: $174.95 - $179.01

================================================================================
Analysis Complete!
================================================================================
```

---

## 🆘 遇到问题？

### 问题1：找不到API文件

**症状**：
```
[ERROR] File not found!
```

**解决**：
```bash
# 检查文件是否存在
dir "C:\Users\lenovo\TradingAgents\"
dir "C:\Users\lenovo\Desktop\new\"
```

### 问题2：API测试失败

**症状**：
```
[FAIL] WRDS
[FAIL] Alpha Vantage
```

**解决**：
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看具体错误信息

### 问题3：系统使用模拟数据

**症状**：
```
[Success] Generated 283 records of mock data
Data Source: Mock Data
```

**说明**：
- 这是正常的
- 所有其他数据源都不可用时使用
- 模拟数据可以正常演示功能

---

## ✅ 检查清单

使用前请确认：

- [ ] 三个API密钥文件都存在
- [ ] `python test_all_apis.py` 测试通过
- [ ] 网络连接正常
- [ ] Python 3.13+ 已安装

---

## 🎉 准备就绪！

**所有检查通过？**

那么你现在可以：

```
双击 accev2.0.01.bat 开始使用！
```

**祝使用愉快！** 🚀

---

*快速启动指南 v2.0.01*
*更新时间: 2026-04-09*
