# API密钥自动加载说明

## 🎯 概述

ACCE v2.0系统会自动从固定位置读取所有API密钥，无需在代码中硬编码。

---

## 📁 API密钥文件位置

所有API密钥文件统一存放在：
```
C:\Users\lenovo\TradingAgents\
```

### 文件列表

| API | 文件路径 | 说明 |
|-----|---------|------|
| **WRDS** | `C:\Users\lenovo\TradingAgents\id.txt` | 学术数据库凭据 |
| **Alpha Vantage** | `C:\Users\lenovo\TradingAgents\av api.txt` | 股票数据API |

---

## 🔑 文件格式说明

### 1. WRDS凭据文件

**位置**: `C:\Users\lenovo\TradingAgents\id.txt`

**格式**：
```
username: hengyang24
password: Appleoppo17@
```

**支持的格式**：
```
# 格式1（冒号分隔）
username: hengyang24
password: Appleoppo17@

# 格式2（等号分隔）
username=hengyang24
password=Appleoppo17@
```

**用途**：
- 访问WRDS学术数据库
- 获取CRSP股票数据
- 获取Compustat财务数据
- **条件**：2024-12-31之前的美股数据自动使用

### 2. Alpha Vantage API密钥文件

**位置**: `C:\Users\lenovo\TradingAgents\av api.txt`

**格式**：
```
01D7TZIVI5LPD54Z
```

**支持的格式**：
```
# 格式1（纯密钥）
01D7TZIVI5LPD54Z

# 格式2（带引号）
"01D7TZIVI5LPD54Z"

# 格式3（带前缀）
api_key=01D7TZIVI5LPD54Z
```

**用途**：
- 获取实时股票数据
- 获取历史价格数据
- **条件**：2024-12-31之后的美股数据
- **限制**：免费版每天25次请求

---

## 🔄 自动加载机制

### 加载顺序

系统按以下顺序查找API密钥：

1. **环境变量**（最高优先级）
   ```python
   os.environ.get("ALPHA_VANTAGE_API_KEY")
   ```

2. **文件读取**（自动降级）
   ```python
   # Alpha Vantage
   C:\Users\lenovo\TradingAgents\av api.txt

   # WRDS
   C:\Users\lenovo\TradingAgents\id.txt
   ```

3. **失败处理**
   - 文件不存在 → 抛出错误
   - 文件格式错误 → 抛出错误
   - 自动降级到下一个数据源

### 代码示例

```python
# Alpha Vantage API加载
api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")

if not api_key:
    # 从文件读取
    if os.path.exists(ALPHA_VANTAGE_API_FILE):
        with open(ALPHA_VANTAGE_API_FILE, 'r') as f:
            content = f.read().strip()
            api_key = content.strip('"').strip("'")
            if '=' in api_key:
                api_key = api_key.split('=', 1)[1].strip()
```

---

## 🧪 测试API密钥

### 方法1：测试Alpha Vantage

创建测试脚本 `test_av_api.py`：

```python
import os

ALPHA_VANTAGE_API_FILE = r"C:\Users\lenovo\TradingAgents\av api.txt"

if os.path.exists(ALPHA_VANTAGE_API_FILE):
    with open(ALPHA_VANTAGE_API_FILE, 'r') as f:
        api_key = f.read().strip().strip('"').strip("'")
        if '=' in api_key:
            api_key = api_key.split('=', 1)[1].strip()

    print(f"Alpha Vantage API Key: {api_key}")
    print(f"Length: {len(api_key)} characters")
else:
    print("API key file not found!")
```

运行：
```bash
python test_av_api.py
```

### 方法2：测试WRDS

运行WRDS测试脚本：
```bash
cd C:\Users\lenovo\Desktop\new
python test_wrds.py
```

---

## 📊 数据源选择逻辑

### 美股历史数据（≤ 2024-12-31）

```
1. WRDS (id.txt) ⭐ 最高优先级
   ↓ 失败
2. Alpha Vantage (av api.txt)
   ↓ 失败
3. yfinance
   ↓ 失败
4. Claw爬虫
   ↓ 失败
5. 模拟数据
```

### 美股实时数据（> 2024-12-31）

```
1. Alpha Vantage (av api.txt)
   ↓ 失败
2. yfinance
   ↓ 失败
3. Claw爬虫
   ↓ 失败
4. 模拟数据
```

---

## ⚙️ 配置步骤

### 1. 获取Alpha Vantage API密钥

1. 访问：https://www.alphavantage.co/support/#api-key
2. 注册免费账号
3. 获取API密钥
4. 保存到 `C:\Users\lenovo\TradingAgents\av api.txt`

### 2. 获取WRDS账号

1. 访问：https://wrds.wharton.upenn.edu/
2. 使用学术邮箱注册
3. 等待账号批准（1-2个工作日）
4. 保存凭据到 `C:\Users\lenovo\TradingAgents\id.txt`

---

## 🔍 故障排除

### Q1: Alpha Vantage连接失败？

**原因**：
- API密钥文件不存在
- API密钥格式错误
- 网络连接问题
- API密钥配额用尽

**解决**：
1. 检查文件是否存在：`C:\Users\lenovo\TradingAgents\av api.txt`
2. 确认文件内容是纯密钥（不要有多余字符）
3. 访问 https://www.alphavantage.co/support/#api-key 检查配额
4. 等待1分钟后重试（免费版限流）

### Q2: WRDS连接失败？

**原因**：
- 凭据文件不存在
- 用户名或密码错误
- 网络无法访问WRDS服务器

**解决**：
1. 检查文件是否存在：`C:\Users\lenovo\TradingAgents\id.txt`
2. 确认格式正确：`username: xxx` 和 `password: xxx`
3. 访问 https://wrds.wharton.upenn.edu/ 手动登录测试
4. 检查网络连接和防火墙设置

### Q3: 两个API都失败了？

**自动降级**：
- 系统会自动尝试yfinance
- 如果yfinance也失败，使用模拟数据
- 不会中断分析流程

---

## ✅ 验证配置

### 完整测试

```bash
cd C:\Users\lenovo\Desktop\new

# 测试WRDS
python test_wrds.py

# 测试完整系统
python run_analysis.py
```

### 期望输出

**WRDS测试**：
```
[OK] WRDS credentials file found!
[OK] Username: hengyang24
[OK] Successfully connected to WRDS!
```

**系统测试**：
```
[WRDS] Connecting to WRDS database as hengyang24...
[Success] Got 283 records from WRDS ***
```

---

## 🔒 安全提示

### 文件权限

确保API密钥文件只有你能访问：

```bash
# Windows
icacls "C:\Users\lenovo\TradingAgents\id.txt" /inheritance:r
icacls "C:\Users\lenovo\TradingAgents\av api.txt" /inheritance:r
```

### 不要提交到版本控制

确保 `.gitignore` 包含：
```
id.txt
av api.txt
*.key
*api.txt
```

---

## 📝 更新日志

### v2.0.01 (2026-04-09)

**新增**：
- ✅ Alpha Vantage API自动加载
- ✅ WRDS凭据自动加载
- ✅ 统一API密钥管理
- ✅ 支持多种文件格式

**改进**：
- ✅ 移除硬编码API密钥
- ✅ 更好的错误处理
- ✅ 自动降级机制

---

## 🎉 总结

**优势**：
- ✅ 集中管理所有API密钥
- ✅ 无需修改代码即可更新密钥
- ✅ 支持多种文件格式
- ✅ 自动加载，透明处理

**文件结构**：
```
C:\Users\lenovo\TradingAgents\
├── id.txt              # WRDS凭据
└── av api.txt          # Alpha Vantage API
```

**现在所有API密钥都自动加载，无需硬编码！** 🚀

---

*更新时间: 2026-04-09*
*版本: v2.0.01*
