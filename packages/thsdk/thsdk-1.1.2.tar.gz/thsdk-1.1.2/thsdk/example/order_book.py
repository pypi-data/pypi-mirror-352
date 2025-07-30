import time
from thsdk import THS, Interval, Adjust
import pandas as pd


def main():
    ths = THS()
    ths_code="USHA600519"
    try:
        # 连接到行情服务器
        response = ths.connect()
        if response.errInfo != "":
            print(f"登录错误:{response.errInfo}")
            return

        response = ths.order_book_ask(ths_code)
        df = pd.DataFrame(response.payload.data)
        print("\n=== 市场深度卖方 ===")
        if df.empty:
            print("没有数据")
        else:
            print(df)

        response = ths.order_book_bid(ths_code)
        df = pd.DataFrame(response.payload.data)
        print("\n=== 市场深度买方 ===")
        if df.empty:
            print("没有数据")
        else:
            print(df)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # 断开连接
        ths.disconnect()
        print("Disconnected from the server.")

    time.sleep(1)


if __name__ == "__main__":
    main()