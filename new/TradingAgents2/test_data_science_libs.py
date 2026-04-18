"""
测试数据科学三件套 + 可视化库
验证pandas, matplotlib, numpy, seaborn, plotly, mplfinance
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from datetime import datetime, timedelta

print("="*70)
print("数据科学库测试")
print("="*70)
print()

# 测试pandas
print("[1/6] Testing pandas...")
df = pd.DataFrame({
    'Date': pd.date_range(start='2024-01-01', periods=10),
    'Price': [100 + i + np.random.randn() for i in range(10)],
    'Volume': np.random.randint(1000000, 10000000, 10)
})
try:
    print(f"[OK] pandas {pd.__version__} - DataFrame created successfully")
    print(f"  Shape: {df.shape}")
except UnicodeEncodeError:
    print(f"[OK] pandas {pd.__version__} - DataFrame created")
    print(f"  Shape: {df.shape}")
print()

# 测试numpy
print("[2/6] Testing numpy...")
arr = np.random.randn(100)
try:
    print(f"[OK] numpy {np.__version__} - Array generated successfully")
    print(f"  Mean: {arr.mean():.4f}")
except UnicodeEncodeError:
    print(f"[OK] numpy {np.__version__}")
    print(f"  Mean: {arr.mean():.4f}")
print()

# 测试matplotlib
print("[3/6] Testing matplotlib...")
try:
    print(f"[OK] matplotlib {matplotlib.__version__}")
except UnicodeEncodeError:
    print(f"[OK] matplotlib {matplotlib.__version__}")

# 创建简单图表
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['Date'], df['Price'], label='Price', linewidth=2)
try:
    ax.set_title('Stock Price Chart', fontsize=14)
except UnicodeEncodeError:
    ax.set_title('Stock Price Chart', fontsize=14)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Price', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

# 保存图表
output_file = 'test_matplotlib_chart.png'
plt.savefig(output_file, dpi=100, bbox_inches='tight')
try:
    print(f"  [OK] Chart saved: {output_file}")
except UnicodeEncodeError:
    print(f"  [OK] Chart saved: {output_file}")
plt.close()
print()

# 测试seaborn
print("[4/6] Testing seaborn...")
try:
    print(f"[OK] seaborn {sns.__version__}")
except UnicodeEncodeError:
    print(f"[OK] seaborn {sns.__version__}")

# 创建seaborn图表
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Price'], kde=True, ax=ax)
try:
    ax.set_title('Price Distribution', fontsize=14)
except UnicodeEncodeError:
    ax.set_title('Price Distribution', fontsize=14)
ax.set_xlabel('Price', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)

# 保存seaborn图表
output_file = 'test_seaborn_chart.png'
plt.savefig(output_file, dpi=100, bbox_inches='tight')
try:
    print(f"  [OK] Seaborn chart saved: {output_file}")
except UnicodeEncodeError:
    print(f"  [OK] Chart saved: {output_file}")
plt.close()
print()

# 测试plotly
print("[5/6] Testing plotly...")
try:
    print(f"[OK] plotly installed")
except UnicodeEncodeError:
    print(f"[OK] plotly installed")

# 创建plotly交互式图表
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Price'],
    mode='lines+markers',
    name='Price',
    line=dict(color='blue', width=2)
))

fig.update_layout(
    title='Stock Price Chart (Plotly)',
    xaxis_title='Date',
    yaxis_title='Price',
    hovermode='x unified'
)

# 保存plotly图表
output_file = 'test_plotly_chart.html'
fig.write_html(output_file)
try:
    print(f"  [OK] Plotly interactive chart saved: {output_file}")
except UnicodeEncodeError:
    print(f"  [OK] Chart saved: {output_file}")
print()

# 测试mplfinance（如果安装了）
try:
    import mplfinance as mpf
    print("[6/6] Testing mplfinance...")
    try:
        print(f"[OK] mplfinance installed")
    except UnicodeEncodeError:
        print(f"[OK] mplfinance installed")

    # 创建OHLC数据格式
    ohlc_df = df.copy()
    ohlc_df.set_index('Date', inplace=True)
    ohlc_df['Open'] = ohlc_df['Price'] * 0.99
    ohlc_df['High'] = ohlc_df['Price'] * 1.02
    ohlc_df['Low'] = ohlc_df['Price'] * 0.98
    ohlc_df['Close'] = ohlc_df['Price']

    # 保存mplfinance图表
    output_file = 'test_mplfinance_chart.png'
    mpf.plot(ohlc_df, type='candle', style='charles', savefig=output_file)
    try:
        print(f"  [OK] mplfinance K-line chart saved: {output_file}")
    except UnicodeEncodeError:
        print(f"  [OK] Chart saved: {output_file}")

except ImportError:
    print("[6/6] mplfinance not installed (optional)")
    print("  Install command: pip install mplfinance")

print()
print("="*70)
print("Test Complete!")
print("="*70)
print()
print("Generated test charts:")
print("  1. test_matplotlib_chart.png - matplotlib static chart")
print("  2. test_seaborn_chart.png - seaborn statistical chart")
print("  3. test_plotly_chart.html - plotly interactive chart")
print("  4. test_mplfinance_chart.png - mplfinance K-line chart (if installed)")
print()
try:
    print("All data science libraries working perfectly!")
except UnicodeEncodeError:
    print("All data science libraries working!")
