"""
修复WRDS连接问题
"""

def get_wrds_data_fixed(ticker, username, password):
    """修复后的WRDS连接"""
    try:
        import wrds

        print(f"[WRDS] 正在连接...")

        # 使用正确的连接方式
        db = wrds.Connection(
            wrds_username=username,
            wrds_password=password,
            auto_connect=True  # 自动连接
        )

        print(f"[WRDS] 连接成功!")

        # 获取数据
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        print(f"[WRDS] 获取 {ticker} 的CRSP数据...")

        # 获取股票数据
        data = db.get_table(
            library='crsp',
            table='dsf',  # 日度股票文件
            columns=['date', 'prc', 'vol', 'ret', 'bid', 'ask'],
            obs_where=f"ticker='{ticker}'",
            cohort_ops={'date': {'gte': start_date.strftime('%Y-%m-%d'),
                                'lte': end_date.strftime('%Y-%m-%d')}},
            limit=10000
        )

        if not data.empty:
            # 重命名列
            data = data.rename(columns={
                'date': 'Date',
                'prc': 'Close',
                'vol': 'Volume',
                'ret': 'Return'
            })

            # 处理数据
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')
            data = data.sort_index()

            # 处理负价格（使用bid ask平均）
            mask = data['Close'] < 0
            if mask.any():
                data.loc[mask, 'Close'] = (data.loc[mask, 'bid'] + data.loc[mask, 'ask']) / 2

            print(f"[成功] 获取到 {len(data)} 条记录")
            print(f"       时间范围: {data.index[0].date()} 到 {data.index[-1].date()}")

            return data
        else:
            print(f"[警告] 未找到 {ticker} 的数据")
            print(f"[提示] 请确认股票代码正确（如AAPL、MSFT等）")
            return None

    except ImportError:
        print("[错误] 请安装WRDS库: pip install wrds")
        return None
    except Exception as e:
        print(f"[错误] WRDS连接失败: {str(e)}")
        print(f"[提示] 可能的原因:")
        print(f"  1. 用户名或密码错误")
        print(f"  2. 网络连接问题")
        print(f"  3. WRDS服务暂时不可用")
        return None

if __name__ == "__main__":
    import pandas as pd

    # 读取账号
    username = "hengyang24"
    password = "Appleoppo17@"

    # 测试连接
    data = get_wrds_data_fixed("AAPL", username, password)

    if data is not None:
        print("\n数据预览:")
        print(data.head())
        print("\n数据统计:")
        print(data.describe())
