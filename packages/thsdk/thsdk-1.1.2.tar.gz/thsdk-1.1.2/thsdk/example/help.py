from thsdk import THS, Interval, Adjust
import pandas as pd
import time


with THS() as ths:
    print("\n=== help about ===")
    print(ths.help("about"))

    print("\n=== help doc ===")
    print(ths.help("doc"))

    print("\n=== help version ===")
    print(ths.help("version"))

    print("\n=== help 空 ===")
    print(ths.help())


    time.sleep(1)

