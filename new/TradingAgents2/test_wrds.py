
import sys
sys.path.insert(0, r"C:\Users\lenovo\TradingAgents")

from tradingagents.dataflows.wrds_source import (
    get_stock_data_wrds,
    get_fundamentals_wrds,
)

def test_wrds():
    print("Testing WRDS connection...")
    from tradingagents.dataflows.wrds_source import get_wrds_connection
    db = get_wrds_connection()
    print("Connected to WRDS successfully\!")
    
    # Test stock data
    print("\nTesting AAPL stock data...")
    result = get_stock_data_wrds("AAPL", "2024-01-01", "2024-12-31")
    print(result[:500])
    
    # Test fundamentals
    print("\nTesting AAPL fundamentals...")
    result = get_fundamentals_wrds("AAPL")
    print(result[:500])

if __name__ == "__main__":
    test_wrds()

