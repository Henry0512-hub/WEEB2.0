"""
自动运行版本 - 分析AAPL股票
"""

import sys
import os

# 模拟用户输入
sys.argv = ['run_analysis.py']  # 添加脚本名

# 导入主程序
import run_analysis

# 执行分析，使用AAPL
print("自动分析AAPL股票...\n")

WRDS_USERNAME = "hengyang24"
WRDS_PASSWORD = "Appleoppo17@"
ticker = "AAPL"

# 尝试WRDS
print(f"[WRDS] 尝试连接WRDS...")
data = run_analysis.get_wrds_data(ticker, WRDS_USERNAME, WRDS_PASSWORD)

if data is None or data.empty:
    print(f"[备用] WRDS失败，使用Yahoo Finance...")
    data = run_analysis.get_yahoo_data(ticker)

if data is None or data.empty:
    print("[错误] 无法获取数据")
    sys.exit(1)

# 执行分析
print("\n" + "=" * 80)
print("开始分析AAPL")
print("=" * 80)

analyzer = run_analysis.StockAnalyzer(data, ticker)
analyzer.clean_and_prepare()
analyzer.analyze()
analyzer.generate_signal()
run_analysis.create_charts(analyzer)
run_analysis.generate_report(analyzer)

# 保存数据
data.to_csv(f"results/{ticker}_data.csv")

print("\n" + "=" * 80)
print("分析完成!")
print("=" * 80)
print(f"\n已生成文件:")
print(f"1. results/{ticker}_analysis.png")
print(f"2. results/{ticker}_report.txt")
print(f"3. results/{ticker}_data.csv")
