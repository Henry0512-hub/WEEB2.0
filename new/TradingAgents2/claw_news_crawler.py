"""
Claw 新闻爬虫 - 使用 crawl4ai 爬取中国新闻网站

支持网站：
- 央视网 (CCTV)
- 新浪财经
- 东方财富
- 证券时报
- 第一财经
"""

import asyncio
from crawl4ai import AsyncWebCrawler
from datetime import datetime
import json
from typing import List, Dict


class ClawNewsCrawler:
    """Claw 新闻爬虫类"""

    def __init__(self):
        self.crawler = None

    async def init(self):
        """初始化爬虫"""
        self.crawler = AsyncWebCrawler(
            headless=True,
            browser_type="chromium",
            verbose=True
        )
        await self.crawler.start()

    async def close(self):
        """关闭爬虫"""
        if self.crawler:
            await self.crawler.close()

    async def crawl_cctv_news(self, limit: int = 10) -> List[Dict]:
        """
        爬取央视新闻

        Args:
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        url = "https://news.cctv.com/"

        try:
            result = await self.crawler.arun(
                url=url,
                word_count_threshold=10,
                extraction_strategy="NoExtraction",
                bypass_cache=True
            )

            if result.success:
                # 解析 HTML 提取新闻
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')

                news_items = []

                # 央视网新闻通常在特定的 div 中
                # 这里需要根据实际页面结构调整选择器
                news_elements = soup.find_all('div', class_='news_item')[:limit]

                for item in news_elements:
                    title_elem = item.find('a')
                    if title_elem:
                        news_items.append({
                            'title': title_elem.get_text(strip=True),
                            'link': title_elem.get('href', ''),
                            'source': 'CCTV',
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

                return news_items
            else:
                try:
                    print(f"爬取失败: {result.error_message}")
                except UnicodeEncodeError:
                    print(f"Crawl failed: {result.error_message}")
                return []

        except Exception as e:
            try:
                print(f"爬取 CCTV 新闻出错: {e}")
            except UnicodeEncodeError:
                print(f"Error crawling CCTV news: {e}")
            return []

    async def crawl_sina_finance(self, limit: int = 10) -> List[Dict]:
        """
        爬取新浪财经新闻

        Args:
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        url = "https://finance.sina.com.cn/"

        try:
            result = await self.crawler.arun(
                url=url,
                word_count_threshold=10,
                bypass_cache=True
            )

            if result.success:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')

                news_items = []

                # 新浪财经新闻选择器
                news_elements = soup.find_all('a', class_='m-p1-md-lst01-a')[:limit]

                for item in news_elements:
                    news_items.append({
                        'title': item.get_text(strip=True),
                        'link': item.get('href', ''),
                        'source': 'Sina Finance',
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                return news_items
            else:
                return []

        except Exception as e:
            try:
                print(f"爬取新浪财经出错: {e}")
            except UnicodeEncodeError:
                print(f"Error crawling Sina Finance: {e}")
            return []

    async def crawl_eastmoney_news(self, limit: int = 10) -> List[Dict]:
        """
        爬取东方财富新闻

        Args:
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        url = "https://www.eastmoney.com/"

        try:
            result = await self.crawler.arun(
                url=url,
                word_count_threshold=10,
                bypass_cache=True
            )

            if result.success:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')

                news_items = []

                # 东方财富新闻选择器
                news_elements = soup.find_all('a', class_='news_item')[:limit]

                for item in news_elements:
                    news_items.append({
                        'title': item.get_text(strip=True),
                        'link': item.get('href', ''),
                        'source': 'Eastmoney',
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                return news_items
            else:
                return []

        except Exception as e:
            try:
                print(f"爬取东方财富出错: {e}")
            except UnicodeEncodeError:
                print(f"Error crawling Eastmoney: {e}")
            return []

    async def crawl_all_sources(self, limit_per_source: int = 5) -> Dict[str, List[Dict]]:
        """
        爬取所有新闻源

        Args:
            limit_per_source: 每个源的新闻数量

        Returns:
            所有新闻的字典
        """
        await self.init()

        try:
            try:
                print("[Claw] 开始爬取中国新闻...\n")
            except UnicodeEncodeError:
                print("[Claw] Starting to crawl Chinese news...\n")

            # 并发爬取所有源
            results = await asyncio.gather(
                self.crawl_cctv_news(limit_per_source),
                self.crawl_sina_finance(limit_per_source),
                self.crawl_eastmoney_news(limit_per_source),
                return_exceptions=True
            )

            all_news = {
                'CCTV': results[0] if not isinstance(results[0], Exception) else [],
                'Sina Finance': results[1] if not isinstance(results[1], Exception) else [],
                'Eastmoney': results[2] if not isinstance(results[2], Exception) else []
            }

            # 统计
            total_news = sum(len(news) for news in all_news.values())
            try:
                print(f"\n[Claw] 爬取完成！共获取 {total_news} 条新闻")
            except UnicodeEncodeError:
                print(f"\n[Claw] Crawl completed! Got {total_news} news")

            for source, news_list in all_news.items():
                try:
                    print(f"  - {source}: {len(news_list)} 条")
                except UnicodeEncodeError:
                    print(f"  - {source}: {len(news_list)} items")

            return all_news

        finally:
            await self.close()

    def format_news_for_llm(self, news_dict: Dict[str, List[Dict]]) -> str:
        """
        将爬取的新闻格式化为 LLM 可读的格式

        Args:
            news_dict: 新闻字典

        Returns:
            格式化的新闻字符串
        """
        output = ["## 中国财经新闻 (Claw 爬虫)\n"]

        for source, news_list in news_dict.items():
            if not news_list:
                continue

            output.append(f"### 来源: {source}\n")

            for news in news_list:
                output.append(f"**{news['title']}**")
                if news.get('link'):
                    output.append(f"链接: {news['link']}")
                output.append("")

        return "\n".join(output)


# 同步版本的便捷函数
def crawl_chinese_news_sync(limit_per_source: int = 5) -> str:
    """
    同步版本：爬取中国新闻

    Args:
        limit_per_source: 每个源的新闻数量

    Returns:
        格式化的新闻字符串
    """
    crawler = ClawNewsCrawler()

    # 运行异步代码
    async def _crawl():
        news_dict = await crawler.crawl_all_sources(limit_per_source)
        return crawler.format_news_for_llm(news_dict)

    try:
        # 在 Windows 上需要设置事件循环策略
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(_crawl())
    except Exception as e:
        try:
            print(f"爬取出错: {e}")
        except UnicodeEncodeError:
            print(f"Crawl error: {e}")
        return f"Crawl failed: {str(e)}"


if __name__ == "__main__":
    print("="*60)
    try:
        print("   Claw 新闻爬虫测试")
    except UnicodeEncodeError:
        print("   Claw News Crawler Test")
    print("="*60)

    # 测试爬取
    news = crawl_chinese_news_sync(limit_per_source=3)

    print("\n" + "="*60)
    try:
        print("   爬取结果")
    except UnicodeEncodeError:
        print("   Crawl Results")
    print("="*60)
    print(news)
