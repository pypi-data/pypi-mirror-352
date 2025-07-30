# import asyncio
# from datetime import datetime, timedelta
# from src.hyperquant.core import Exchange
# from src.hyperquant.datavison.coinglass import CoinglassApi


# async def main():
#     api = CoinglassApi()
#     await api.connect()
#     df = await api.fetch_price_klines('Binance_BTCUSDT', datetime.now() - timedelta(days=1))
#     print(df)
#     await api.stop()

# if __name__ == '__main__':
#     asyncio.run(main())


import asyncio
from datetime import datetime, timedelta
from hyperquant.datavison.binance import BinanceSwap
from hyperquant.broker.hyperliquid import HyperliquidTrader

async def test1():
    symbol = "BTCUSDT"
    interval = "1m"
    # 取最近10分钟的K线
    end_time = int(time.time() * 1000)
    start_time = end_time - 10 * 60 * 1000
    swap = BinanceSwap()


    # 新增时间参数例子
    start_date = datetime.now() - timedelta(minutes=5)
    end_date = datetime.now()
    klines = await swap.get_index_klines(symbol, interval, start_date, end_date)

    print(klines)

    await swap.session.close()

async def test2():
    async with HyperliquidTrader() as trader:
        # 获取当前账户信息
        print(
            await trader.get_mid('FEUSD', True)
        )


if __name__ == "__main__":
    import time

    asyncio.run(test2())