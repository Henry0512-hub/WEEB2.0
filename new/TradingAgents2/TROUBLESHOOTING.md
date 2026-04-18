# 使用指南和故障排除

## 🚀 正确使用方法

### ⚠️ 重要提示
系统需要在**本地交互式终端**中运行，不能在后台运行！

### 方法1：使用Windows PowerShell（推荐）

1. 按 `Win + X`，选择 "Windows PowerShell"
2. 运行以下命令：
   ```powershell
   cd C:\Users\lenovo\TradingAgents
   python run_crypto_trading.py
   ```
3. 然后按提示输入：
   ```
   请输入加密货币代码: ETH
   请输入分析日期: [直接回车]
   ```

### 方法2：使用桌面脚本

1. 双击桌面上的 **`启动TradingAgents加密货币版.bat`**
2. 选择选项 1
3. 输入币种代码和日期

---

## ✅ 支持的加密货币列表

### 主流币种（推荐）
- **BTC** - 比特币
- **ETH** - 以太坊
- **BNB** - 币安币
- **SOL** - Solana
- **XRP** - 瑞波币

### DeFi 代币
- **UNI** - Uniswap
- **AAVE** - Aave
- **LINK** - Chainlink

### 公链项目
- **ADA** - Cardano
- **AVAX** - Avalanche
- **DOT** - Polkadot
- **MATIC** - Polygon
- **ATOM** - Cosmos

### 其他热门
- **DOGE** - 狗狗币
- **OP** - Optimism
- **ARB** - Arbitrum

---

## ⚠️ 常见错误和解决方案

### 错误1: Error code: 404

**原因**：
- 输入的币种代码不在支持列表中
- CoinGecko API不支持该币种

**解决**：
1. 检查币种代码是否正确（必须大写，如 BTC 而不是 btc）
2. 使用支持列表中的币种
3. 运行检查工具：`python check_crypto_support.py`

### 错误2: SSL Error / Connection Error

**原因**：
- 网络连接不稳定
- VPN连接问题

**解决**：
1. 检查VPN是否正常工作
2. 测试API连接：`python test_network.py`
3. 尝试其他币种（如ETH、BNB）
4. 等待几分钟后重试

### 错误3: API 余额不足

**原因**：
- DeepSeek API余额耗尽

**解决**：
1. 访问 https://platform.deepseek.com/
2. 充值账户余额
3. 检查API使用情况

---

## 🔍 诊断工具使用

### 1. 检查币种是否支持
```bash
python check_crypto_support.py
```
然后输入币种代码，查看是否支持

### 2. 测试网络连接
```bash
python test_network.py
```
检查CoinGecko API是否可访问

### 3. 测试API密钥
```bash
python test_api_key.py
```
验证DeepSeek API是否可用

---

## 💡 最佳实践

### 首次使用建议

1. **先用ETH测试**（最稳定）
   ```
   请输入加密货币代码: ETH
   ```

2. **使用今天日期**
   ```
   请输入分析日期: [直接回车]
   ```

3. **等待分析完成**
   - 首次运行可能需要3-5分钟
   - 请保持耐心，不要中断

### 节省API调用

降低辩论轮数可以节省API费用，编辑 `run_crypto_trading.py`:

```python
config["max_debate_rounds"] = 1  # 降低到1轮
config["max_risk_discuss_rounds"] = 1
```

---

## 📊 查看分析结果

分析完成后，结果会保存在：
```
results/trading_signals/
├── ETH_20250107_143022.json
└── ETH_20250107_143022.txt
```

查看TXT文件获取可读的报告。

---

## 🆘 仍然遇到问题？

1. **检查VPN** - 确保VPN已开启并正常工作
2. **使用ETH** - 先用以太坊测试，最稳定
3. **查看日志** - 检查 `results/` 目录下的日志文件
4. **重启程序** - 关闭后重新运行

---

## 📞 快速参考

**成功运行的命令**：
```bash
cd C:\Users\lenovo\TradingAgents
python run_crypto_trading.py
```

**输入示例**：
```
加密货币代码: ETH
日期: [回车]
```

**推荐首次测试币种**：
- ETH（以太坊）- 最稳定
- BNB（币安币）- 测试通过
- SOL（Solana）- 热门

---

祝使用愉快！🚀
