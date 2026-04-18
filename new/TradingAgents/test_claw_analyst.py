"""
测试 Claw 新闻爬虫
"""

print("="*70)
print("   Claw 新闻爬虫 - 测试脚本")
print("="*70)

print("\n正在测试 Claw 新闻爬虫功能...\n")

# 首先安装 playwright 浏览器（如果还没安装）
print("[步骤 1] 检查 playwright 浏览器")

try:
    import subprocess
    result = subprocess.run(
        ["playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("[OK] playwright 浏览器已就绪")
    else:
        print("[INFO] 正在安装 playwright 浏览器...")
        print("这可能需要几分钟...")
except:
    print("[INFO] 首次运行需要安装浏览器")

print("\n[步骤 2] 测试 Claw 爬虫")

try:
    from claw_news_crawler import crawl_chinese_news_sync

    print("正在爬取中国新闻（每个源 3 条）...")
    print("请稍候...\n")

    news = crawl_chinese_news_sync(limit_per_source=3)

    if news and "爬取失败" not in news:
        print("[OK] Claw 爬虫测试成功！\n")
        print("="*70)
        print("爬取的新闻内容：")
        print("="*70)
        print(news)
        print("="*70)

        print("\n[统计] 成功爬取中国新闻")
        print("[建议] 可以集成到 TradingAgents 中使用")

    else:
        print("[WARNING] 爬取结果为空或失败")
        print("可能的原因：")
        print("1. 网络连接问题")
        print("2. 目标网站结构变化")
        print("3. 防爬虫机制")
        print("\n建议：查看上方错误信息")

except Exception as e:
    print(f"[ERROR] 测试失败: {e}")
    print("\n排查建议：")
    print("1. 确保网络连接正常")
    print("2. 检查是否需要安装浏览器：playwright install chromium")
    print("3. 查看完整错误信息")

print("\n[步骤 3] 测试 Claw 新闻分析师集成")

try:
    from tradingagents.agents.analysts.claw_news_analyst import create_claw_news_analyst
    from langchain_openai import ChatOpenAI

    print("\n创建测试 LLM...")
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        temperature=0.7
    )

    print("创建 Claw 新闻分析师...")
    claw_analyst = create_claw_news_analyst(llm)

    print("[OK] Claw 新闻分析师创建成功！")
    print("\n现在可以在 TradingAgents 中使用 Claw 新闻分析师了")

except Exception as e:
    print(f"[ERROR] 集成测试失败: {e}")

print("\n" + "="*70)
print("   测试完成")
print("="*70)

print("\n下一步：")
print("1. 如果测试成功，运行完整分析：")
print("   python run_with_claw_analyst.py")
print("\n2. 如果测试失败，检查：")
print("   - 网络连接")
print("   - 目标网站可访问性")
print("   - 防火墙设置")

print("\nClaw 新闻爬虫的优势：")
print("✓ 实时爬取中国财经新闻")
print("✓ 覆盖多个本土新闻源")
print("✓ 无需 API Key")
print("✓ 完全免费")
print("✓ 可自定义新闻源")
