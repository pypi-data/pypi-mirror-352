from thsdk import THS, Interval, Adjust
import pandas as pd
import time


with THS() as ths:
    # 查询历史近100条日k数据
    response = ths.download("USHA600519", count=100)
    print(pd.DataFrame(response.payload.data))


    # 查询历史20240101 - 202050101 日k数据
    # response = ths.download("USHA600519", start=20240101, end=20250101)
    # print(pd.DataFrame(response.payload.data))

    # 查询历史所有日k数据
    # response = ths.download("USHA600519")
    # print(pd.DataFrame(response.payload.data))

    # 查询历史100条日k数据 前复权
    # response = ths.download("USHA600519", count=100, adjust=Adjust.FORWARD)
    # print(pd.DataFrame(response.payload.data))

    # 查询历史100跳1分钟k数据
    response = ths.download("USHA600519", count=100, interval=Interval.MIN_1)
    print(pd.DataFrame(response.payload.data))
    time.sleep(1)

