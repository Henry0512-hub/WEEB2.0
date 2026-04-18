# Simple WRDS Data Viewer
import sys
sys.path.insert(0, r'C:\Users\lenovo\TradingAgents')

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.interface import route_to_vendor

# Set WRDS config
config = {
    ''data_vendors'': {
        ''core_stock_apis'': ''wrds'',
        ''fundamental_data'': ''wrds'',
    },
    ''tool_vendors'': {
        ''get_stock_data'': ''wrds'',
        ''get_fundamentals'': ''wrds'',
    }
}
set_config(config)

ticker = ''AAPL''
start_date = ''2023-06-01''
end_date = ''2023-06-12''

print(f''Analyzing {ticker}...'')
print()

# Stock data
print('Stock Data (WRDS CRSP):')
result = route_to_vendor('get_stock_data', ticker, start_date, end_date)
print(result)

# Fundamentals  
print('Fundamentals (WRDS Compustat):')
result = route_to_vendor('get_fundamentals', ticker)
print(result)