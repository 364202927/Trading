import sys,os
from data.user.assetsCenter import assetsCenter
from core.manage import run


# binance
#获取btc 2020-01-01 ~ 2天后的数据
# ex_binance.historical_Candle('BTC/USDT', '2020-01-01', 2)
#获取btc 2020-01-01 ~ 2020-01-03的数据
# ex_binance.historical_Candle('BTC/USDT', '2020-01-01', '2020-01-02',save2File = True)
#获取多组，多时间间隔 数据
# ex_binance.historical_Candle(['BTC/USDT','ETH/USDT'], start_time = '2020-01-01', end_time = 5, timeFrameOrTab = ['30m'],save2File = True)
#交易所全文件记录到文件
# ex_binance.historical_Candle('all', start_time = '2020-01-01', timeFrameOrTab = '30m', save2File = True)
# okex
# ex_okex.historical_Candle(['BTC/USDT','ETH/USDT'], start_time = '2021-01-01', end_time = 5, timeFrameOrTab = ['15m','30m'], save2File = True)
# ex_okex.historical_Candle('all', '2021-01-01', '2021-01-02',save2File = True)

#合约
# 币安 BTCUSDT BTCUSD_PERP   u本位币本位
# okex BTC-USDT-211210 交割  BTC-USDT-SWAP永续
# ex_binance.fhistorical_Candle(["BTCUSDT",'BTCUSD_PERP'],'2021-01-01',10, timeFrameOrTab = ['30m'], save2File = True)
# ex_okex.fhistorical_Candle(['BTC-USDT-SWAP','BTC-USDT-211210'],'2021-11-30','2021-12-05',timeFrameOrTab = ['5m','15m'], save2File = True)


def main():
	user = assetsCenter()
	ex_binance = user.getExchange("binance")
	ex_okex = user.getExchange("okex3")



if __name__ == "__main__":
	main()