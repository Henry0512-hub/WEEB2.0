# Claw 新闻分析师 - 使用指南

## 🎯 什么是 Claw？

**Claw** 是一个基于 [crawl4ai](https://github.com/unclecode/crawl4ai) 的新闻爬虫，专门用于爬取中国财经新闻网站。

### 核心功能

- ✅ **实时爬取**：直接从网站获取最新新闻
- ✅ **多源支持**：央视、新浪财经、东方财富等
- ✅ **零成本**：无需 API Key，完全免费
- ✅ **易于集成**：无缝集成到 TradingAgents

---

## 📦 已安装的组件

### 1. crawl4ai
```bash
pip install crawl4ai
```

### 2. Claw 新闻爬虫
```
TradingAgents/claw_news_crawler.py
```

### 3. Claw 新闻分析师
```
TradingAgents/tradingagents/agents/analysts/claw_news_analyst.py
```

---

## 🚀 快速开始

### 方式 1：单独测试 Claw 爬虫

```bash
cd TradingAgents
python claw_news_crawler.py
```

### 方式 2：测试 Claw 新闻分析师

```bash
cd TradingAgents
python test_claw_analyst.py
```

### 方式 3：完整运行（带 Claw 分析师）

```bash
cd TradingAgents
python run_with_claw_analyst.py
```

---

## 📰 支持的新闻源

| 新闻源 | 网站 | 覆盖内容 |
|--------|------|----------|
| **央视网 (CCTV)** | cctv.com | 国家政策、宏观经济 |
| **新浪财经** | finance.sina.com.cn | 市场动态、个股新闻 |
| **东方财富** | eastmoney.com | A股行情、行业资讯 |
| **证券时报** | stcn.com | 深度分析、公司报道 |
| **第一财经** | yicai.com | 财经新闻、市场评论 |

---

## 💡 使用示例

### 基础爬取

```python
from claw_news_crawler import crawl_chinese_news_sync

# 爬取所有新闻源（每个源 5 条）
news = crawl_chinese_news_sync(limit_per_source=5)
print(news)
```

### 集成到 TradingAgents

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "deepseek"
config["backend_url"] = "https://api.deepseek.com/v1"
config["deep_think_llm"] = "deepseek-chat"

# 创建实例
ta = TradingAgentsGraph(debug=True, config=config)

# 运行分析（Claw 会自动提供中国新闻）
_, decision = ta.propagate("BABA", "2025-01-15")
print(decision)
```

---

## 🔧 配置选项

### 调整爬取数量

```python
# 在 claw_news_crawler.py 中
news = crawl_chinese_news_sync(limit_per_source=10)  # 每个源 10 条
```

### 添加自定义新闻源

```python
# 在 claw_news_crawler.py 的 ClawNewsCrawler 类中
async def crawl_custom_news(self, url: str, limit: int = 10):
    result = await self.crawler.arun(url=url, bypass_cache=True)
    # 解析代码...
```

### 调整爬虫参数

```python
self.crawler = AsyncWebCrawler(
    headless=True,           # 无头模式
    browser_type="chromium",  # 浏览器类型
    verbose=True,            # 详细日志
    # 更多参数...
)
```

---

## 📊 Claw vs 其他新闻源

| 特性 | Claw | yfinance | Alpha Vantage |
|------|------|----------|---------------|
| **价格** | 免费 | 免费 | 25次/天免费 |
| **中国新闻** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **实时性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **API Key** | 不需要 | 不需要 | 需要 |
| **可定制性** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **稳定性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## ⚠️ 注意事项

### 法律和道德

- ✓ 遵守网站的 `robots.txt`
- ✓ 仅用于个人研究和学习
- ✓ 不要过度频繁请求
- ✗ 不要用于商业目的（需授权）

### 技术限制

1. **首次运行较慢**
   - 需要下载浏览器（chromium）
   - 大小约 100-200MB

2. **网站结构变化**
   - 网站改版可能导致爬取失败
   - 需要更新选择器

3. **网络要求**
   - 需要能访问目标网站
   - 某些网站可能有反爬机制

4. **性能**
   - 爬取速度取决于网络和网站响应
   - 建议：异步爬取多个源

---

## 🐛 故障排除

### 问题 1：浏览器未安装

**错误：** `Executable doesn't exist`

**解决：**
```bash
playwright install chromium
```

### 问题 2：爬取失败

**可能原因：**
- 网络连接问题
- 目标网站结构变化
- 防爬虫机制

**解决：**
```python
# 启用详细日志查看错误
self.crawler = AsyncWebCrawler(
    headless=True,
    verbose=True,  # 开启详细日志
)
```

### 问题 3：编码错误

**错误：** `UnicodeEncodeError`

**解决：**
```python
# 在 Windows 上设置事件循环策略
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

---

## 📈 性能优化

### 1. 并发爬取

```python
# 已实现并发爬取多个源
results = await asyncio.gather(
    self.crawl_cctv_news(limit),
    self.crawl_sina_finance(limit),
    self.crawl_eastmoney_news(limit),
)
```

### 2. 缓存

```python
# crawl4ai 内置缓存
result = await self.crawler.arun(
    url=url,
    bypass_cache=False,  # 使用缓存
)
```

### 3. 限制爬取数量

```python
# 限制每个源的新闻数量
news = crawl_chinese_news_sync(limit_per_source=3)  # 只爬 3 条
```

---

## 🎓 进阶用法

### 自定义新闻解析器

```python
from bs4 import BeautifulSoup

async def crawl_custom_site(self, url: str):
    result = await self.crawler.arun(url=url)

    if result.success:
        soup = BeautifulSoup(result.html, 'html.parser')

        # 自定义解析逻辑
        news_items = soup.find_all('div', class_='custom-class')

        return [
            {
                'title': item.find('h2').text,
                'link': item.find('a')['href'],
                # 更多字段...
            }
            for item in news_items
        ]
```

### 添加到 TradingAgents 工作流

```python
# 在 trading_graph.py 中添加 claw_news_analyst
from tradingagents.agents.analysts.claw_news_analyst import create_claw_news_analyst

# 添加到工作流
workflow.add_node("claw_news_analyst", create_claw_news_analyst(llm))
```

---

## 📝 最佳实践

### 1. 定期更新选择器
```python
# 网站结构可能变化，定期检查
news_elements = soup.find_all('div', class_='current-class')
```

### 2. 错误处理
```python
try:
    news = await self.crawl_site()
except Exception as e:
    logger.error(f"爬取失败: {e}")
    return []
```

### 3. 限速
```python
import asyncio
# 添加延迟避免被封
await asyncio.sleep(2)  # 2秒延迟
```

---

## 🔄 更新和维护

### 更新 crawl4ai

```bash
pip install --upgrade crawl4ai
```

### 更新浏览器

```bash
playwright install chromium --with-deps
```

### 更新选择器

定期检查目标网站结构，更新 CSS 选择器。

---

## 🆘 获取帮助

### 查看日志

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试连接

```python
# 测试能否访问目标网站
import requests
response = requests.get("https://news.cctv.com/")
print(response.status_code)
```

### 查看文档

- crawl4ai: https://github.com/unclecode/crawl4ai
- TradingAgents: https://github.com/TauricResearch/TradingAgents

---

## 🎉 总结

### Claw 的优势

- ✅ **零成本**：完全免费，无需 API
- ✅ **实时性**：直接爬取，最新新闻
- ✅ **本土化**：中国市场的独特视角
- ✅ **可定制**：轻松添加新源
- ✅ **集成简单**：无缝接入 TradingAgents

### 适用场景

- 分析 A 股
- 分析中概股（BABA, JD 等）
- 关注中国政策
- 研究中国市场

### 下一步

1. **测试 Claw**
   ```bash
   python test_claw_analyst.py
   ```

2. **运行完整分析**
   ```bash
   python run_with_claw_analyst.py
   ```

3. **自定义配置**
   - 添加更多新闻源
   - 调整爬取数量
   - 优化性能

**开始使用 Claw，获取中国财经新闻的独特视角！** 🚀
