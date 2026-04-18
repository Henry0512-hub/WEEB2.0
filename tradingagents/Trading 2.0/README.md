# Trading 2.0

与仓库根目录 **同一套 ACCE 能力**；默认 **无额外限制**（含加密货币与智能路由）。

可选：若需「无加密货币」环境，启动前设置：

```bash
set TRADING20_NO_CRYPTO=1
python "Trading 2.0/start_web.py"
```

## 启动 Web

```bash
pip install -r web_requirements.txt
python "Trading 2.0/start_web.py"
```

## 启动 CLI

```bash
python "Trading 2.0/start_cli.py"
```

说明：`start_web.py` / `run_analysis_web.py` 会先 `import` 本目录的 `bootstrap`；若未设置 `TRADING20_NO_CRYPTO`，`apply_no_crypto_patch()` 为空操作。
