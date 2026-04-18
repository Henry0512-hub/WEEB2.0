# 更换API密钥指南

## 📝 步骤1：编辑配置文件

打开文件：`C:\Users\lenovo\TradingAgents\api_config.py`

将你的新API密钥粘贴到 `DEEPSEEK_API_KEY` 变量中：

```python
# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-你的新API密钥粘贴在这里"  # 修改这行
```

保存文件。

---

## 🧪 步骤2：测试新密钥

在命令行运行：

```bash
cd C:\Users\lenovo\TradingAgents
python test_api_key.py
```

如果看到 "测试完成！API密钥工作正常"，说明密钥有效。

---

## 🚀 步骤3：启动系统

### 方法A：使用桌面脚本
双击桌面的 `启动TradingAgents加密货币版.bat`

### 方法B：命令行启动
```bash
python run_crypto_trading.py
```

---

## ⚠️ 常见问题

### Q1: API密钥在哪里获取？
**A:** 访问 https://platform.deepseek.com/ 注册并获取API密钥

### Q2: 测试提示余额不足？
**A:** 需要充值DeepSeek账户余额，购买API调用额度

### Q3: 如何查看API使用情况？
**A:** 登录DeepSeek平台查看账户余额和使用记录

### Q4: 可以使用其他API吗？
**A:** 可以，修改配置文件支持OpenAI、Claude等

---

## 📊 节省API调用的方法

1. **减少辩论轮数**
   编辑 `run_crypto_trading.py`:
   ```python
   config["max_debate_rounds"] = 1  # 降低到1轮
   config["max_risk_discuss_rounds"] = 1
   ```

2. **使用更快的模型**
   ```python
   config["deep_think_llm"] = "deepseek-chat"  # 使用便宜的模型
   ```

3. **先测试再运行**
   使用简单的测试确保配置正确

---

需要帮助？查看 `CRYPTO_TRADING_GUIDE.md` 获取完整使用指南！
