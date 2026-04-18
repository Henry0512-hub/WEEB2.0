# ACCE v2.0 - 完整API配置说明

## 🎯 概述

ACCE v2.0系统**自动加载所有API密钥**，无需在代码中硬编码。所有密钥统一存放在固定位置。

---

## 📁 API密钥文件位置

### 文件结构

```
C:\Users\lenovo\TradingAgents\
├── id.txt              # WRDS学术数据库凭据
└── av api.txt          # Alpha Vantage API密钥

C:\Users\lenovo\Desktop\new\
└── api assents.txt     # LLM API密钥（DeepSeek, Kimi, Gemini）
```

---

## 🔑 文件格式说明

### 1. WRDS凭据 (id.txt)

**位置**: `C:\Users\lenovo\TradingAgents\id.txt`

**格式**:
```
username: hengyang24
password: Appleoppo17@
```

**支持的格式**:
```
# 格式1（冒号分隔）✅ 推荐
username: hengyang24
password: Appleoppo17@

# 格式2（等号分隔）
username=hengyang24
password=Appleoppo17@
```

**用途**:
- 访问WRDS学术数据库
- 获取CRSP股票数据
- **优先级**: 2024-12-31之前的美股数据自动使用 ⭐

---

### 2. Alpha Vantage API (av api.txt)

**位置**: `C:\Users\lenovo\TradingAgents\av api.txt`

**格式**:
```
01D7TZIVI5LPD54Z
```

**支持的格式**:
```
# 格式1（纯密钥）✅ 推荐
01D7TZIVI5LPD54Z

# 格式2（带引号）
"01D7TZIVI5LPD54Z"

# 格式3（带前缀）
api_key=01D7TZIVI5LPD54Z
```

**用途**:
- 获取实时股票数据
- **优先级**: 2024-12-31之后的美股数据
- **限制**: 免费版每天25次请求

---

### 3. LLM APIs (api assents.txt) ⭐ 新增

**位置**: `C:\Users\lenovo\Desktop\new\api assents.txt`

**格式**:
```
deepseek: sk-aa0ac23b61974015826717b2ba86dec3
kimi: sk-zuVM5fhu24KzBytPVhcz8lF6k37GNqXnZcQRAwgfj3GBeN53
gemini: AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk
```

**支持的格式**:
```
# 格式1（冒号分隔）✅ 推荐
deepseek: sk-xxx
kimi: sk-xxx
gemini: xxx

# 格式2（逗号分隔）
deepseek, sk-xxx
kimi, sk-xxx

# 格式3（等号分隔）
deepseek=sk-xxx
kimi=sk-xxx
```

**说明**:
- `deepseek`: DeepSeek API密钥（推荐，最便宜）
- `kimi`: Kimi API密钥（中文支持最好）
- `gemini`: Google Gemini API密钥（免费1500次/天）

---

## 🔄 自动加载机制

### 加载顺序

```
1. 环境变量（最高优先级，可覆盖）
   ↓ 未设置
2. 文件读取（自动加载）
   ↓ 文件不存在
3. 错误提示（明确告知缺少哪个API）
```

### 代码示例

```python
# LLM API加载
def load_llm_api_keys():
    api_keys = {}
    with open(LLM_API_FILE, 'r') as f:
        for line in f:
            # 支持多种分隔符
            if ':' in line:
                key, value = line.split(':', 1)
            elif ',' in line:
                key, value = line.split(',', 1)
            api_keys[key.strip().lower()] = value.strip()
    return api_keys

# 使用
api_keys = load_llm_api_keys()
deepseek_key = api_keys.get("deepseek")
```

---

## 📊 数据源优先级

### 美股历史数据（≤ 2024-12-31）⭐

```
1. WRDS (id.txt) ⭐ 最高准确性
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

## 🧪 测试工具

### 完整API测试

```bash
cd C:\Users\lenovo\Desktop\new
python test_all_apis.py
```

**测试内容**:
- ✅ WRDS凭据读取和连接
- ✅ Alpha Vantage API读取和调用
- ✅ LLM APIs读取（DeepSeek, Kimi, Gemini）

**期望输出**:
```
================================================================================
                   ACCE v2.0 - API Keys Test
================================================================================

================================================================================
Testing WRDS Credentials
================================================================================
[OK] File found!
[OK] Username: hengyang24
[OK] Password: ************
[Testing] Connecting to WRDS...
[OK] Successfully connected to WRDS!

================================================================================
Testing Alpha Vantage API
================================================================================
[OK] File found!
[OK] API Key: 01D7TZIVI...54Z
[Testing] API call...
[OK] API key is valid!

================================================================================
Testing LLM API Keys (DeepSeek, Kimi, Gemini)
================================================================================
[OK] File found!
[OK] Loaded 3 LLM API key(s):
     - DEEPSEEK: sk-aa0ac2...N53
     - KIMI: sk-zuVM5f...BeN53
     - GEMINI: AIzaSyA...Sld-Euk

================================================================================
Test Summary
================================================================================
  [PASS] WRDS
  [PASS] Alpha Vantage
  [PASS] LLM APIs

[SUCCESS] All API keys are configured correctly!
```

---

## ⚙️ 配置步骤

### 1. 获取API密钥

#### WRDS（学术数据库）
1. 访问：https://wrds.wharton.upenn.edu/
2. 使用学术邮箱注册
3. 等待批准（1-2个工作日）
4. 保存到 `C:\Users\lenovo\TradingAgents\id.txt`

#### Alpha Vantage
1. 访问：https://www.alphavantage.co/support/#api-key
2. 注册免费账号
3. 获取API密钥
4. 保存到 `C:\Users\lenovo\TradingAgents\av api.txt`

#### DeepSeek（推荐）
1. 访问：https://platform.deepseek.com/
2. 注册账号
3. 获取API密钥
4. 保存到 `C:\Users\lenovo\Desktop\new\api assents.txt`

#### Kimi（月之暗面）
1. 访问：https://platform.moonshot.cn/
2. 注册账号
3. 获取API密钥
4. 保存到 `C:\Users\lenovo\Desktop\new\api assents.txt`

#### Gemini（Google）
1. 访问：https://aistudio.google.com/
2. 注册账号
3. 获取API密钥
4. 保存到 `C:\Users\lenovo\Desktop\new\api assents.txt`

---

## 🔍 故障排除

### Q1: LLM API加载失败？

**原因**:
- 文件不存在
- 格式不正确
- 缺少必需的API密钥

**解决**:
1. 检查文件是否存在：`C:\Users\lenovo\Desktop\new\api assents.txt`
2. 确认格式：`deepseek: sk-xxx`（冒号分隔）
3. 运行测试：`python test_all_apis.py`

### Q2: 某个LLM API不可用？

**系统行为**:
- 系统会提示缺少哪个API
- 不会中断程序，但该分析师不可用
- 建议配置DeepSeek（最便宜）

### Q3: 所有API都失败了？

**自动降级**:
- 数据获取会降级到yfinance或模拟数据
- LLM分析将无法使用
- 建议至少配置一个LLM API

---

## ✅ 验证配置

### 快速验证

```bash
# 测试所有API
python test_all_apis.py

# 测试系统
python run_analysis.py
```

### 检查清单

- [ ] WRDS凭据文件存在且格式正确
- [ ] Alpha Vantage API文件存在
- [ ] LLM API文件存在且包含至少一个API
- [ ] 所有API测试通过

---

## 🎉 总结

### 新功能（v2.0.01）

✅ **统一API管理** - 所有密钥集中存放
✅ **自动加载** - 无需手动配置
✅ **灵活格式** - 支持多种分隔符
✅ **错误提示** - 明确告知缺失哪个API
✅ **完整测试** - 一键测试所有API

### API密钥文件汇总

| API | 文件位置 | 格式示例 |
|-----|---------|---------|
| WRDS | `C:\Users\lenovo\TradingAgents\id.txt` | `username: xxx` |
| Alpha Vantage | `C:\Users\lenovo\TradingAgents\av api.txt` | `01D7TZIVI5LPD54Z` |
| DeepSeek | `C:\Users\lenovo\Desktop\new\api assents.txt` | `deepseek: sk-xxx` |
| Kimi | `C:\Users\lenovo\Desktop\new\api assents.txt` | `kimi: sk-xxx` |
| Gemini | `C:\Users\lenovo\Desktop\new\api assents.txt` | `gemini: xxx` |

### 优势

**安全性**:
- ✅ 密钥不在代码中
- ✅ 可以设置文件权限
- ✅ 易于添加到 `.gitignore`

**便捷性**:
- ✅ 统一位置管理
- ✅ 无需修改代码
- ✅ 支持多种格式

---

**现在所有API密钥都自动加载，配置完成后即可使用！** 🚀

---

*更新时间: 2026-04-09*
*版本: v2.0.01*
