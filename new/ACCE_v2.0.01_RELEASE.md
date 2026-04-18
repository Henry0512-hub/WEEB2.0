# ACCE v2.0.01 - Release Notes

## 🎉 新版本发布

**版本号**: v2.0.01
**发布日期**: 2026-04-09
**系统名称**: ACCE (Analysis Center for Capital Markets)

---

## 📋 本次更新内容

### 1. 新的系统架构 ⭐

**文件结构**:
```
C:\Users\lenovo\Desktop\
├── accev2.0.01.bat          # 新启动器（统一命名）
└── new\                     # 核心文件目录
    ├── intelligent_data_fetcher.py    # 智能数据获取器
    ├── run_analysis.py                # 主分析程序
    ├── test_wrds.py                   # WRDS测试工具
    └── README.md                      # 系统说明

C:\Users\lenovo\TradingAgents\
└── id.txt                   # WRDS凭据（固定位置）
```

### 2. WRDS优先级设置 ⭐⭐⭐

**核心功能**:
- ✅ 2024-12-31之前的美股数据**自动优先使用WRDS**
- ✅ 固定WRDS凭据位置：`C:\Users\lenovo\TradingAgents\id.txt`
- ✅ 每次启动自动连接WRDS
- ✅ WRDS不可用时自动降级到其他数据源

**优先级规则**:
```
美股历史数据（≤ 2024-12-31）:
  1. WRDS学术数据库 ⭐ (最高准确性)
  2. Alpha Vantage
  3. yfinance
  4. Claw爬虫
  5. 模拟数据
```

### 3. 智能数据源路由

**自动判断逻辑**:
```python
if (美股 AND 日期 ≤ 2024-12-31):
    使用WRDS ⭐
elif (中概股):
    使用akshares
else:
    使用Alpha Vantage / yfinance
```

### 4. 多LLM分析师支持

**可选分析师**:
1. **DeepSeek** (推荐)
   - 价格：¥1/百万tokens
   - API: sk-d28ae30a58cb496c9b40e0029d0ef2c1

2. **Kimi** (中文优化)
   - 价格：付费
   - API: sk-PBksAJzkTW48yH12moqKci3hckekib80qJzMz63MG4XVfPyd

3. **Gemini** (免费)
   - 价格：免费（1500次/天）
   - API: AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk

### 5. 统一版本命名

**命名规则**: `accev2.0.0x.bat`

- `acce`: 系统名称
- `v2.0`: 主版本号
- `0x`: 子版本号（01, 02, 03...）

---

## 🚀 使用方法

### 启动系统

1. **双击启动器**
   ```
   accev2.0.01.bat
   ```

2. **选择分析师**
   ```
   1 - DeepSeek (推荐)
   2 - Kimi
   3 - Gemini
   ```

3. **输入股票代码**
   ```
   AAPL, TSLA, NVDA, etc.
   ```

4. **输入日期范围**
   ```
   开始日期: 2024-06-15
   结束日期: 2024-08-15
   ```

5. **自动分析**
   - 系统自动选择数据源
   - WRDS优先（如适用）
   - 显示数据摘要

---

## 📊 数据源优先级详情

### 场景1：美股历史数据（≤ 2024-12-31）⭐

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| **1** | **WRDS** | 学术数据库，最高准确性 |
| 2 | Alpha Vantage | 备选API |
| 3 | yfinance | 免费数据 |
| 4 | Claw爬虫 | 互联网爬取 |
| 5 | 模拟数据 | 最后备选 |

**示例**:
```
股票: AAPL
日期: 2024-06-15 到 2024-08-15
结果: 自动使用WRDS ⭐
```

### 场景2：美股实时数据（> 2024-12-31）

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| 1 | Alpha Vantage | 实时数据 |
| 2 | yfinance | 免费数据 |
| 3 | Claw爬虫 | 互联网爬取 |
| 4 | 模拟数据 | 最后备选 |

**示例**:
```
股票: TSLA
日期: 2025-01-15 到 2025-03-20
结果: 使用Alpha Vantage
```

### 场景3：中概股

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| 1 | akshares | 中国市场专用 |
| 2 | yfinance | 国际数据 |
| 3 | Claw爬虫 | 互联网爬取 |
| 4 | 模拟数据 | 最后备选 |

**示例**:
```
股票: BABA
日期: 任意
结果: 使用akshares
```

---

## ⚙️ 配置说明

### WRDS凭据

**位置**: `C:\Users\lenovo\TradingAgents\id.txt`

**格式**:
```
username=your_wrds_username
password=your_wrds_password
```

**测试**:
```bash
cd C:\Users\lenovo\Desktop\new
python test_wrds.py
```

### Alpha Vantage API

**位置**: 内置在启动器中

**Key**: `01D7TZIVI5LPD54Z`

**限制**: 每天25次免费请求

---

## 🔧 测试工具

### WRDS连接测试

```bash
cd C:\Users\lenovo\Desktop\new
python test_wrds.py
```

**功能**:
- ✅ 检查凭据文件是否存在
- ✅ 验证凭据格式是否正确
- ✅ 测试WRDS连接
- ✅ 执行测试查询

---

## 📝 版本管理

### 当前版本

**v2.0.01** (2026-04-09)
- ✅ WRDS优先级设置
- ✅ 固定凭据位置
- ✅ 智能数据源路由
- ✅ 统一命名规范

### 未来版本

**v2.0.02** (规划中)
- [ ] 完整A股支持
- [ ] 新闻情绪分析
- [ ] 技术指标计算

**v2.1.0** (规划中)
- [ ] Web界面
- [ ] 实时数据流
- [ ] 机器学习预测

---

## 🎯 技术亮点

### 1. 学术级数据质量

通过优先使用WRDS，系统可以获得：
- ⭐ CRSP数据库：经过专业清洗的股价数据
- ⭐ Compustat数据库：标准化财务数据
- ⭐ 无前瞻性偏差：适合回测和研究
- ⭐ 学术认可：论文发表级数据质量

### 2. 智能降级机制

```
WRDS → Alpha Vantage → yfinance → Claw → 模拟数据
```

即使某个数据源失败，系统仍能继续工作。

### 3. 透明化处理

系统会明确显示：
- ✅ 使用的数据源
- ✅ 数据获取状态
- ✅ 数据质量摘要
- ✅ 降级过程

---

## 💡 使用建议

### 学术研究

```
使用WRDS数据（2024-12-31之前）
→ 确保数据准确性
→ 发表级数据质量
→ 适合论文和回测
```

### 实时分析

```
使用Alpha Vantage/yfinance
→ 获取最新数据
→ 快速决策支持
→ 适合日常交易
```

### 演示展示

```
使用模拟数据
→ 快速生成结果
→ 无需复杂配置
→ 适合教学演示
```

---

## 📚 相关文档

- `C:\Users\lenovo\Desktop\new\README.md` - 系统使用说明
- `C:\Users\lenovo\Desktop\new\test_wrds.py` - WRDS测试工具
- `C:\Users\lenovo\TradingAgents\WRDS_PRIORITY_GUIDE.md` - WRDS详细指南

---

## ⚠️ 注意事项

### WRDS访问

- **需要学术账号**：只有学术机构可以访问
- **并发限制**：同时连接数有限
- **数据延迟**：历史数据更新有1-2天延迟

### 自动降级

WRDS不可用时，系统会自动使用其他数据源，无需手动干预。

### 数据源选择

**建议**：
- 学术研究/回测 → WRDS
- 实时分析 → Alpha Vantage
- 快速演示 → 模拟数据

---

## 🎊 总结

### 新系统优势

✅ **学术级数据** - WRDS提供最高准确性
✅ **智能路由** - 自动判断数据源
✅ **自动降级** - 确保系统稳定
✅ **统一命名** - 便于版本管理
✅ **固定配置** - WRDS凭据集中管理

### 适用场景

| 场景 | 数据源 | 日期范围 |
|------|--------|---------|
| 学术研究 | WRDS | ≤ 2024-12-31 |
| 论文回测 | WRDS | ≤ 2024-12-31 |
| 实时分析 | Alpha Vantage | > 2024-12-31 |
| 日常使用 | yfinance | 任意日期 |

---

**ACCE v2.0.01 - 让数据分析更简单、更准确！** 🚀📊

---

*发布时间: 2026-04-09*
*版本号: v2.0.01*
*系统: ACCE Analysis System*
