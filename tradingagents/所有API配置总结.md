# TradingAgents - 所有 LLM API 配置完成

## 🎉 恭喜！现在你有 4 个可用的 LLM API

### 1. ✅ DeepSeek API（推荐使用）
```
API Key: sk-d28ae30a58cb496c9b40e0029d0ef2c1
价格: ¥1/百万tokens（最便宜）
模型: deepseek-chat, deepseek-reasoner
运行: python run_with_deepseek.py
```

### 2. ✅ Gemini API（Google）
```
API Key: AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk
价格: 免费（每天 1,500 次）
模型: gemini-2.5-flash, gemini-2.5-pro
运行: python run_with_gemini.py
限制: 需要能访问 Google
```

### 3. ✅ Kimi API（月之暗面）
```
API Key: sk-PBksAJzkTW48yH12moqKci3hckekib80qJzMz63MG4XVfPyd
价格: 付费（新用户有免费额度）
模型: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
运行: python run_with_kimi.py
优势: 中文支持最好，128k 长上下文
```

### 4. ✅ 其他国产大模型（可配置）
- 智谱 GLM（完全免费）
- 通义千问（100万tokens/月免费）
- 百度文心（100万tokens免费）
- 讯飞星火（新用户免费）

## 📊 四大 API 对比

| API | 价格 | 速度 | 中文 | 网络要求 | 推荐度 |
|-----|------|------|------|----------|--------|
| **DeepSeek** | ¥1/百万 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 直接访问 | ⭐⭐⭐⭐⭐ |
| **Kimi** | 付费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 直接访问 | ⭐⭐⭐⭐⭐ |
| **Gemini** | 免费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 需翻墙 | ⭐⭐⭐⭐ |
| **GLM** | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 直接访问 | ⭐⭐⭐⭐ |

## 🚀 快速开始

### 推荐 1：DeepSeek（性价比最高）
```bash
cd TradingAgents
python run_with_deepseek.py
```

### 推荐 2：Kimi（中文最好）
```bash
cd TradingAgents
python run_with_kimi.py
```

### 免费：Gemini（需要翻墙）
```bash
cd TradingAgents
python run_with_gemini.py
```

### 使用 CLI
```bash
cd TradingAgents
tradingagents
```

## 🎯 使用场景推荐

### 日常生产环境：DeepSeek
```python
config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
```
**原因**：最便宜，稳定，中文好

### 中文任务：Kimi
```python
config["llm_provider"] = "openai"
config["backend_url"] = "https://api.moonshot.cn/v1"
config["deep_think_llm"] = "moonshot-v1-8k"
```
**原因**：中文理解最深入，128k 上下文

### 测试学习：Gemini
```python
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.5-flash"
```
**原因**：免费额度多，推理能力强

### 长文本分析：Kimi 128k
```python
config["deep_think_llm"] = "moonshot-v1-128k"
```
**原因**：支持 128k 超长上下文

## 💡 组合使用策略

### 策略 1：快速任务用 Gemini，深度推理用 DeepSeek
```python
config["llm_provider"] = "deepseek"
config["quick_think_llm"] = "gemini-2.5-flash-lite"  # 通过自定义配置
config["deep_think_llm"] = "deepseek-chat"
```

### 策略 2：中文用 Kimi，英文用 Gemini
```python
# 中文分析
config["deep_think_llm"] = "moonshot-v1-8k"
config["output_language"] = "Chinese"

# 英文分析
config["deep_think_llm"] = "gemini-2.5-flash"
config["output_language"] = "English"
```

### 策略 3：降低成本 - 全用便宜的
```python
config["llm_provider"] = "deepseek"
config["deep_think_llm"] = "deepseek-chat"
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
```

## 📝 测试脚本

```bash
# 测试 DeepSeek
python test_deepseek_simple.py

# 测试 Gemini
python test_gemini_simple.py

# 测试 Kimi
python test_kimi.py
```

## 🔧 快速切换 API

### 切换到 DeepSeek
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-d28ae30a58cb496c9b40e0029d0ef2c1"

config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"
```

### 切换到 Kimi
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-PBksAJzkTW48yH12moqKci3hckekib80qJzMz63MG4XVfPyd"

config["llm_provider"] = "openai"
config["backend_url"] = "https://api.moonshot.cn/v1"
config["deep_think_llm"] = "moonshot-v1-8k"
```

### 切换到 Gemini
```python
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyAIOWEahqzuBZV5Ne7sm_IylWrzSld-Euk"

config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.5-flash"
```

## 🎓 我的个人推荐

### 最省心：DeepSeek
- 便宜：¥1/百万tokens
- 稳定：国内可直接访问
- 快速：响应速度快
- 中文：中文支持好

### 中文最好：Kimi
- 理解：中文理解最深入
- 长文本：128k 上下文
- 稳定：国内服务
- 质量：输出质量高

### 免费学习：Gemini
- 免费：每天 1500 次
- 强大：Google 技术加持
- 快速：响应非常快
- 限制：需要翻墙

## 📊 API 余额查询

- **DeepSeek**: https://platform.deepseek.com/
- **Gemini**: https://aistudio.google.com/
- **Kimi**: https://platform.moonshot.cn/console

## 🎯 下一步

1. **运行第一次分析**
   ```bash
   python run_with_deepseek.py
   ```

2. **尝试不同股票**
   - 美股: AAPL, TSLA, NVDA
   - 中概股: BABA, JD, BIDU
   - 港股: 0700.HK, 9988.HK

3. **集成 akshare**
   - 获取更好的中国股市数据

4. **优化配置**
   - 调整辩论轮数
   - 选择合适的模型
   - 切换输出语言

## 🆘 遇到问题？

### DeepSeek 无法连接
- 检查 API Key 是否正确
- 确认网络连接正常
- 查询账户余额

### Gemini 无法连接
- 确认能访问 Google
- 检查 API Key
- 确认未超出免费额度

### Kimi 无法连接
- 检查 API Key
- 确认账户有余额
- 查看官方文档

## 📚 相关文档

- `使用指南.md` - 基础使用指南
- `配置总结.md` - 配置说明
- `获取Gemini密钥指南.md` - Gemini 获取指南

## 🎉 总结

你现在拥有：
- ✅ 3 个已配置的 LLM API（DeepSeek, Gemini, Kimi）
- ✅ 完整的 TradingAgents 框架
- ✅ 多个运行示例脚本
- ✅ 测试脚本验证连接

**建议从 DeepSeek 开始，它最稳定可靠！**

```bash
cd TradingAgents
python run_with_deepseek.py
```

祝使用愉快！🎊
