import time
from thsdk import THS, Interval, Adjust
import pandas as pd

with THS() as ths:
    response = ths.wencai_nlp("龙头行业;国资委;所属行业")
    df = pd.DataFrame(response.payload.data)
    print(df)

    time.sleep(1)


def main():
    ths = THS()
    try:
        # 连接到行情服务器
        response = ths.connect()
        if response.errInfo != "":
            print(f"登录错误:{response.errInfo}")
            return

        response = ths.wencai_nlp("龙头行业;国资委;所属行业")
        df = pd.DataFrame(response.payload.data)
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
