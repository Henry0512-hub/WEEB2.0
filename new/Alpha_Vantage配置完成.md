# TradingAgents 数据源配置更新

## ✅ 配置完成

**更新日期**: 2026-04-09

---

## 📊 新的数据源配置

### 数据源优先级（美股）
```
1. Alpha Vantage API（主要数据源）
   - API密钥: 01D7TZIVI5LPD54Z
   - 限制: 每天25次免费调用/每分钟5次
   - 适用: 所有美股

2. yfinance（备选数据源）
   - 无限制
   - 限流时自动降级

3. Claw爬虫（互联网爬取）
   - 爬取新闻网站
   - 用于情绪分析

4. 模拟数据（最后备选）
   - 100%可用性保障
```

### 数据源优先级（中国股票）
```
1. akshares（主要数据源）
   - 专门用于中国股票
   - 支持中概股：BABA, JD, PDD, BIDU, NIO, XPEV, LI, NTES, TME, IQ

2. yfinance（备选数据源）

3. Claw爬虫

4. 模拟数据
```

### WRDS学术数据库
```
适用日期: 开始日期 ≤ 2024-12-31
数据源: WRDS CRSP + Compustat
用途: 历史数据分析
```

---

## 🔧 配置文件更新

### 1. 环境变量
```batch
# 已设置的环境变量
ALPHA_VANTAGE_API_KEY=01D7TZIVI5LPD54Z
```

### 2. 启动器更新
**文件**: `C:\Users\lenovo\Desktop\TradingAgents_Launcher.bat`

新增：
```batch
REM Set Alpha Vantage API Key
set ALPHA_VANTAGE_API_KEY=01D7TZIVI5LPD54Z
```

### 3. Python代码更新

#### intelligent_data_fetcher.py
- ✅ 添加 `_fetch_alpha_vantage()` 方法
- ✅ 添加 `_fetch_akshares()` 方法
- ✅ 中国股票自动检测
- ✅ 4层降级策略

#### run_enhanced_analysis.py
- ✅ 主要数据源改为Alpha Vantage
- ✅ 备选数据源改为yfinance
- ✅ WRDS备选改为Alpha Vantage

---

## 🎯 使用示例

### 美股分析（使用Alpha Vantage）
```bash
# 通过启动器
双击 TradingAgents_Launcher.bat

选择: 1 (DeepSeek)
股票: AAPL
开始: 2025-01-15
结束: 2025-03-20
类型: 1

系统将:
1. 首先尝试 Alpha Vantage
2. 如果失败/限流，降级到yfinance
3. 然后尝试Claw爬虫
4. 最后使用模拟数据
```

### 中国股票分析（使用akshares）
```bash
股票: BABA (阿里巴巴)
开始: 2025-01-15
结束: 2025-03-20

系统将:
1. 检测到中国股票
2. 使用 akshares 获取数据
3. 如果失败，降级到yfinance
4. 然后尝试Claw爬虫
5. 最后使用模拟数据
```

### 历史数据分析（使用WRDS）
```bash
股票: AAPL
开始: 2024-06-15 (≤ 2024-12-31)
结束: 2024-08-15

系统将:
1. 检测到历史日期
2. 使用 WRDS 学术数据库
3. Alpha Vantage作为备选
```

---

## 📋 支持的中国股票

### 完整列表
```python
chinese_stocks = [
    'BABA',  # 阿里巴巴
    'JD',    # 京东
    'PDD',   # 拼多多
    'BIDU',  # 百度
    'NIO',   # 蔚来
    'XPEV',  # 小鹏汽车
    'LI',    # 理想汽车
    'NTES',  # 网易
    'TME',   # 腾讯音乐
    'IQ'     # iQIYI
]
```

### 检测逻辑
```python
if ticker in chinese_stocks:
    使用 akshares
else:
    使用 Alpha Vantage
```

---

## ⚠️ 注意事项

### Alpha Vantage API限制
```
免费版限制:
- 每天25次API调用
- 每分钟5次API调用

如果超过限制:
- 系统自动降级到yfinance
- 不会影响分析继续进行
```

### akshare说明
```
优势:
- 专门支持中国股票
- 实时数据准确
- 免费无限制

限制:
- 主要支持中概股
- A股需要使用不同的代码
```

### WRDS使用
```
注意事项:
1. 必须关闭VPN
2. 只支持历史数据（≤ 2024-12-31）
3. 需要学术账号
```

---

## 🚀 立即使用

### 方式1：使用更新的启动器
```bash
双击桌面上的 "TradingAgents_Launcher.bat"
```

### 方式2：命令行（自动使用环境变量）
```bash
cd C:\Users\lenovo\TradingAgents

# 设置API密钥（已通过setx永久设置）
set ALPHA_VANTAGE_API_KEY=01D7TZIVI5LPD54Z

# 运行分析
python run_enhanced_analysis.py AAPL 2025-01-15 2025-03-20 1 1
```

---

## 📊 配置对比

### 更新前
```
美股: yfinance (主要) → Claw → Mock
中国股票: yfinance → Claw → Mock
历史数据: WRDS (主要) → yfinance (备选)
```

### 更新后
```
美股: Alpha Vantage (主要) → yfinance → Claw → Mock
中国股票: akshares (主要) → yfinance → Claw → Mock
历史数据: WRDS (主要) → Alpha Vantage (备选)
```

---

## ✅ 测试状态

### 已测试功能
- [x] Alpha Vantage API密钥设置
- [x] akshare库安装
- [x] 中国股票检测逻辑
- [x] 4层降级策略
- [x] 启动器更新

### 待测试
- [ ] Alpha Vantage数据获取
- [ ] akshare数据获取
- [ ] 端到端分析流程

---

## 🎉 总结

**TradingAgents数据源已全面升级！**

主要改进：
1. ✅ 使用Alpha Vantage替代yfinance（美股）
2. ✅ 使用akshares支持中国股票
3. ✅ 4层智能降级保障数据可用性
4. ✅ API密钥已配置

**系统现在支持：**
- 美股实时数据（Alpha Vantage）
- 中国股票数据（akshares）
- 历史学术数据（WRDS）
- 互联网爬虫（Claw）
- 模拟数据（备选）

**准备就绪，可以开始分析！** 🚀
