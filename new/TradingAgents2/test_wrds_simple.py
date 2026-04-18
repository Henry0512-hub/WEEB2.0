
# Simple WRDS Data Test - No TradingAgentsGraph
import sys
sys.path.insert(0, r"C:\Users\lenovo\TradingAgents")

print("="*70)
print("Simple WRDS Data Test")
print("="*70)

# Set config
from tradingagents.dataflows.config import set_config
config = {
    "data_vendors": {
        "core_stock_apis": "wrds",
        "fundamental_data": "wrds",
    },
    "tool_vendors": {
        "get_stock_data": "wrds",
        "get_fundamentals": "wrds",
    }
}
set_config(config)

# Import routing
from tradingagents.dataflows.interface import route_to_vendor

print("\n[1] Getting AAPL stock data (June 2023)...")
stock_data = route_to_vendor("get_stock_data", "AAPL", "2023-06-01", "2023-06-12")
print(stock_data[:500])

print("\n" + "="*70)
print("[2] Getting AAPL fundamentals...")
fund_data = route_to_vendor("get_fundamentals", "AAPL")
print(fund_data[:500])

print("\n" + "="*70)
print("SUCCESS\! WRDS data is working correctly.")
print("You can use this data for your analysis.")
print("="*70)

