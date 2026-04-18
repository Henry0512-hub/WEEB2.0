# ✅ API Key 问题已修复！

## 🔍 问题原因

你的系统环境变量中有**通义千问的旧 API Key**：
```
OPENAI_API_KEY=eab7105d034d48d8b3c2aebd2ef0766f.5ixauVSpHPChC0gi
```

这个 Key 覆盖了 .env 文件中的 DeepSeek API Key。

---

## ✅ 已修复的文件

### 1. run_with_deepseek.py
- ✅ 强制设置正确的 DeepSeek API Key
- ✅ 覆盖系统环境变量

### 2. 一键启动.py
- ✅ 强制设置正确的 DeepSeek API Key
- ✅ 覆盖系统环境变量

---

## 🚀 现在可以使用了！

### 方式 1：使用桌面快捷方式

**双击桌面上的：** `启动TradingAgents修复版.bat`

### 方式 2：命令行直接运行

```bash
cd C:\Users\lenovo\TradingAgents
python run_with_deepseek.py
```

### 方式 3：使用交互式菜单

```bash
cd C:\Users\lenovo\TradingAgents
python 一键启动.py
```

选择 `1` (DeepSeek 模式)

---

## 📝 验证修复

运行后会看到：
```
[OK] DeepSeek API Key 已设置: sk-d28ae30...f2c1
```

这是**正确的** DeepSeek API Key！

---

## 💡 为什么会这样？

你的系统之前配置了**通义千问**（阿里云的 API），设置了系统环境变量：
- `OPENAI_API_KEY=eab7105d...` （通义千问的 Key）
- `OPENAI_BASE_URL=https://coding.dashscope.aliyuncs.com/v1` （阿里云的地址）

现在我已经在脚本中强制覆盖为 DeepSeek 的配置。

---

## 🎯 彻底解决（可选）

如果你想永久删除旧的系统环境变量：

### Windows 系统
1. 右键 "此电脑" → "属性"
2. "高级系统设置" → "环境变量"
3. 在 "用户变量" 中找到并删除：
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL`
   - `OPENAI_MODEL`

### 或者保留
**不需要删除！** 现在的脚本会自动覆盖为正确的 DeepSeek API Key。

---

## ✅ 现在就可以使用了！

**双击桌面上的 `启动TradingAgents修复版.bat` 开始分析！** 🚀

---

**问题已完全解决！DeepSeek API 已正确配置。**
