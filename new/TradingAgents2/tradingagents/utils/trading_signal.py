"""
交易推荐信号处理模块

用于提取、格式化和保存交易推荐信号
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class TradingSignal:
    """交易信号类"""

    RATING_MAP = {
        "Buy": "强力买入",
        "Overweight": "增持",
        "Hold": "持有",
        "Underweight": "减持",
        "Sell": "卖出"
    }

    def __init__(self, ticker: str, decision_text: str, timestamp: str = None):
        """
        初始化交易信号

        Args:
            ticker: 资产代码
            decision_text: 决策文本
            timestamp: 时间戳
        """
        self.ticker = ticker.upper()
        self.raw_decision = decision_text
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.rating = self._extract_rating()
        self.summary = self._extract_summary()
        self.thesis = self._extract_thesis()

    def _extract_rating(self) -> Optional[str]:
        """从决策文本中提取评级"""
        for rating in ["Buy", "Overweight", "Hold", "Underweight", "Sell"]:
            # 匹配 **Rating**: Buy 或 **Buy**: 等格式
            patterns = [
                rf"\*\*Rating\*\*:\s*\*?\*?{rating}\*?\*?",
                rf"\*\*{rating}\*\*:",
                rf"Rating:\s*{rating}",
                rf"Recommendation:\s*{rating}",
            ]
            for pattern in patterns:
                if re.search(pattern, self.raw_decision, re.IGNORECASE):
                    return rating
        return None

    def _extract_summary(self) -> str:
        """提取执行摘要"""
        # 查找 Executive Summary 或 Summary 部分
        patterns = [
            r"\*\*Executive Summary\*\*:?\s*\n(.*?)(?=\n\n|\*\*|\Z)",
            r"\*\*Summary\*\*:?\s*\n(.*?)(?=\n\n|\*\*|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, self.raw_decision, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "未找到摘要"

    def _extract_thesis(self) -> str:
        """提取投资论点"""
        # 查找 Investment Thesis 部分
        patterns = [
            r"\*\*Investment Thesis\*\*:?\s*\n(.*?)(?=\n\n|\*\*|\Z)",
            r"\*\*Thesis\*\*:?\s*\n(.*?)(?=\n\n|\*\*|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, self.raw_decision, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "未找到投资论点"

    def get_cn_rating(self) -> str:
        """获取中文评级"""
        if self.rating:
            return self.RATING_MAP.get(self.rating, self.rating)
        return "未定"

    def format_signal(self) -> str:
        """格式化交易信号为易读格式"""
        signal = []
        signal.append("=" * 70)
        signal.append(f"[交易推荐] 交易推荐信号 - {self.ticker}")
        signal.append("=" * 70)
        signal.append(f"[时间] 时间: {self.timestamp}")
        signal.append("")

        # 评级部分
        if self.rating:
            rating_symbol = {
                "Buy": "[强力买入]",
                "Overweight": "[增持]",
                "Hold": "[持有]",
                "Underweight": "[减持]",
                "Sell": "[卖出]"
            }.get(self.rating, "[未定]")

            signal.append(f"{rating_symbol} **推荐评级**: {self.rating} ({self.get_cn_rating()})")
            signal.append("")

        # 执行摘要
        signal.append("[摘要] **执行摘要**:")
        signal.append("-" * 70)
        signal.append(self.summary)
        signal.append("")

        # 投资论点
        signal.append("[论点] **投资论点**:")
        signal.append("-" * 70)
        signal.append(self.thesis[:500] + "..." if len(self.thesis) > 500 else self.thesis)
        signal.append("")

        signal.append("=" * 70)

        return "\n".join(signal)

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "ticker": self.ticker,
            "timestamp": self.timestamp,
            "rating": self.rating,
            "rating_cn": self.get_cn_rating(),
            "summary": self.summary,
            "thesis": self.thesis,
            "raw_decision": self.raw_decision
        }

    def save_to_file(self, results_dir: str = "./results"):
        """保存信号到文件"""
        # 创建目录
        signal_dir = Path(results_dir) / "trading_signals"
        signal_dir.mkdir(parents=True, exist_ok=True)

        # 保存JSON格式
        json_file = signal_dir / f"{self.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        # 保存文本格式（易读）
        txt_file = signal_dir / f"{self.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(self.format_signal())

        return json_file, txt_file


def parse_trading_signal(ticker: str, decision_text: str, timestamp: str = None) -> TradingSignal:
    """
    解析交易信号

    Args:
        ticker: 资产代码
        decision_text: 决策文本
        timestamp: 时间戳

    Returns:
        TradingSignal: 交易信号对象
    """
    return TradingSignal(ticker, decision_text, timestamp)


def display_trading_recommendation(ticker: str, decision_text: str, save: bool = True):
    """
    显示交易推荐

    Args:
        ticker: 资产代码
        decision_text: 决策文本
        save: 是否保存到文件
    """
    signal = parse_trading_signal(ticker, decision_text)

    # 打印格式化的推荐
    print(signal.format_signal())

    # 保存到文件
    if save:
        json_file, txt_file = signal.save_to_file()
        print()
        print("[保存] 信号已保存:")
        print(f"  JSON: {json_file}")
        print(f"  TXT:  {txt_file}")

    return signal


if __name__ == "__main__":
    # 测试代码
    test_decision = """
**Rating**: **Buy**

**Executive Summary**:
Based on strong technical momentum and positive fundamental developments, we recommend entering a long position in BTC. Current support at $42,000 provides a favorable risk-reward setup. Suggested position size: 2-3% of portfolio. Stop loss: $40,000. Target: $50,000.

**Investment Thesis**:
Bitcoin shows strong bullish momentum with increasing institutional adoption. Technical indicators show the asset is trading above key moving averages with positive RSI divergence...
"""

    signal = parse_trading_signal("BTC", test_decision)
    print(signal.format_signal())
    print("\n\n转换为字典:")
    print(json.dumps(signal.to_dict(), ensure_ascii=False, indent=2))
