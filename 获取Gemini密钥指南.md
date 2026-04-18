# 获取 Google Gemini API Key 详细步骤

## 📝 步骤 1：访问 Google AI Studio

打开浏览器，访问：
```
https://aistudio.google.com/app/apikey
```

## 🔑 步骤 2：创建 API Key

1. **登录 Google 账号**
   - 如果没有，需要先注册一个

2. **点击 "Create API Key" 按钮**
   - 页面上会有一个大按钮

3. **选择或创建项目**
   - 可以选择现有项目
   - 或创建新项目（推荐：创建一个名为 "TradingAgents" 的项目）

4. **复制 API Key**
   - 格式类似：`AIzaSyxxxxxxxxxxxxxxxxxxxxxxx`
   - 以 `AIza` 开头

5. **保存 API Key**
   - 安全保存，不要分享给他人

## ⚠️ 注意事项

- **网络要求**：需要能访问 Google（可能需要科学上网）
- **免费额度**：
  - 每天：1,500 次请求
  - 每月：慷慨的免费额度
- **适用模型**：
  - Gemini 2.5 Flash（推荐）
  - Gemini 2.5 Flash Lite
  - Gemini 2.5 Pro
  - Gemini 1.5 Flash

## 🔧 获取 API Key 后

回到 TradingAgents 目录，运行：
```bash
cd C:\Users\lenovo\TradingAgents
python setup_gemini.py
```

输入你获取的 API Key 即可自动配置。

## 🧪 测试 API Key

配置后，运行测试：
```bash
python test_gemini.py
```

## 💡 如果无法访问 Google

考虑使用其他方案：
1. **DeepSeek**（你现在有）- 性价比高，中国可访问
2. **智谱 GLM** - 国产，完全免费
3. **通义千问** - 阿里云，100万免费tokens/月
