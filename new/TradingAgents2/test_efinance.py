import efinance as ef
import pandas as pd

print('Testing efinance with different date formats...')
print()

# Test 1: With beg/end parameters
print('Test 1: With beg/end parameters')
data1 = ef.stock.get_quote_history('000001', beg='2024-12-01', end='2024-12-31')
print(f'Type: {type(data1)}, Empty: {data1.empty if hasattr(data1, "empty") else "N/A"}')
if not data1.empty:
    print(f'Shape: {data1.shape}')
    print(f'Columns: {list(data1.columns)}')
    print(f'\nFirst 3 rows:\n{data1.head(3)}')
print()

# Test 2: Without date parameters
print('Test 2: Without date parameters (get all data)')
data2 = ef.stock.get_quote_history('000001')
print(f'Type: {type(data2)}, Empty: {data2.empty if hasattr(data2, "empty") else "N/A"}')
if not data2.empty:
    print(f'Shape: {data2.shape}')
    # Filter for recent data
    data2['日期'] = pd.to_datetime(data2['日期'])
    recent = data2[data2['日期'] >= '2024-12-01'].sort_values('日期', ascending=False)
    print(f'Recent data (Dec 2024+): {recent.shape}')
    print(f'\nMost recent 3 rows:\n{recent.head(3)}')
