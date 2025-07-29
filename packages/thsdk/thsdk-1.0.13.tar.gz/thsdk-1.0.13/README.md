# thsdk

# Installation

```bash
pip install --upgrade thsdk
```

# Usage

### 日k数据查询

```python
from thsdk import THS
import pandas as pd

with THS() as ths:
    response = ths.download("USHA600519", count=100)
    print(pd.DataFrame(response.payload.data))


```

### Result:

```
          time    close   volume    turnover     open     high      low
0   2024-12-11  1535.60  2967112  4569662600  1540.00  1555.00  1530.98
1   2024-12-12  1565.80  4193652  6510547800  1532.02  1566.00  1529.00
2   2024-12-13  1519.00  4951197  7580908300  1550.01  1554.99  1518.88
3   2024-12-16  1527.20  3253710  4945298800  1521.00  1529.00  1510.71
4   2024-12-17  1558.00  5417163  8398945400  1525.99  1569.00  1521.01
..         ...      ...      ...         ...      ...      ...      ...
96  2025-05-09  1591.18  2367190  3757574500  1578.99  1597.45  1575.05
97  2025-05-12  1604.50  2473533  3967785800  1598.00  1618.93  1596.61
98  2025-05-13  1590.30  2125829  3386617800  1608.92  1608.92  1585.11
99  2025-05-14  1634.99  3946012  6394735100  1590.00  1645.00  1588.18
100 2025-05-15  1636.66  1534953  2509610500  1634.80  1643.59  1624.13

[101 rows x 7 columns]
```

### 获取市场数据

```python
from thsdk import THS
import pandas as pd

with THS() as ths:
    response = ths.get_block_data(0xE)
    df = pd.DataFrame(response.payload.data)
    usza_codes = df[df['代码'].str.startswith('USZA')]['代码'].tolist()
    response = ths.stock_market_data(usza_codes)
    print(pd.DataFrame(response.payload.data))



```

### Result:

```
         价格  成交方向      成交量       量比  ...    跌停价    最高价    最低价    开盘涨幅
0     13.50     5   170000   4.9043  ...  12.10  13.56  13.41  0.6696
1      4.00     5   506000   1.9396  ...   3.57   4.01   3.97  0.2519
2     16.10     0  1685512   6.0916  ...  12.80  16.16  15.91 -0.1875
3     19.51     1   191900   1.5161  ...  17.73  19.71  19.45  0.0000
4     22.05     1  2327556   4.2304  ...  20.00  22.27  22.00 -0.8101
...     ...   ...      ...      ...  ...    ...    ...    ...     ...
2864   1.89     1  1471300   7.6000  ...   1.53   1.91   1.89 -0.5236
2865   9.38     1  2839900  22.0322  ...   9.30   9.55   9.30 -5.0051
2866   1.95     1  2063600   7.0924  ...   1.88   1.98   1.95 -0.5051
2867   4.96     5  1331800   2.3004  ...   4.68   4.98   4.94  0.2028
2868   3.41     5  3603800   4.8005  ...   3.28   3.41   3.36 -2.0290

[2869 rows x 28 columns]
```

```python
from thsdk import THS
import pandas as pd

with THS() as ths:
    # 查询历史近100条日k数据
    response = ths.download("USHA600519", count=100)

    # 查询历史20240101 - 202050101 日k数据
    # response = ths.download("USHA600519", start=20240101, end=20250101)

    # 查询历史所有日k数据
    # response = ths.download("USHA600519")

    # 查询历史100条日k数据 前复权
    # response = ths.download("USHA600519", count=100, adjust=Adjust.FORWARD)

    # 查询历史100跳1分钟k数据
    # response = ths.download("USHA600519", count=100, interval=Interval.MIN_1)

    # 问财查询
    # response = ths.wencai_base("所属概念")

    # 问财AI
    # response = ths.wencai_nlp("涨停;所属概念")

    # 帮助
    # print(ths.help("about","help"))

    print(pd.DataFrame(response.payload.data))


```

### Result:

```
         time    close   volume    turnover     open     high      low
0   2024-01-02  1685.01  3215644  5440082500  1715.00  1718.19  1678.10
1   2024-01-03  1694.00  2022929  3411400700  1681.11  1695.22  1676.33
2   2024-01-04  1669.00  2155107  3603970100  1693.00  1693.00  1662.93
3   2024-01-05  1663.36  2024286  3373155600  1661.33  1678.66  1652.11
4   2024-01-08  1643.99  2558620  4211918600  1661.00  1662.00  1640.01
..         ...      ...      ...         ...      ...      ...      ...
237 2024-12-25  1530.00  1712339  2621061900  1538.80  1538.80  1526.10
238 2024-12-26  1527.79  1828651  2798840000  1534.00  1538.78  1523.00
239 2024-12-27  1528.97  2075932  3170191400  1528.90  1536.00  1519.50
240 2024-12-30  1525.00  2512982  3849542600  1533.97  1543.96  1525.00
241 2024-12-31  1524.00  3935445  6033540400  1525.40  1545.00  1522.01

[242 rows x 7 columns]
```

```python
from thsdk import THS, Adjust, Interval
import pandas as pd


def main():
    with THS() as ths:
        # 获取历史日级别数据
        response = ths.security_bars("USHA600519", 20240101, 20250420, Adjust.NONE, Interval.DAY)

        if response.errInfo != "":
            print(f"查询错误:{response.errInfo}")
            return

        df = pd.DataFrame(response.payload.data)
        print(df)
        print("查询成功 数量:", len(response.payload.data))


if __name__ == "__main__":
    main()


```

### Result:

```
          time    close   volume    turnover     open     high      low
0   2024-01-02  1685.01  3215644  5440082500  1715.00  1718.19  1678.10
1   2024-01-03  1694.00  2022929  3411400700  1681.11  1695.22  1676.33
2   2024-01-04  1669.00  2155107  3603970100  1693.00  1693.00  1662.93
3   2024-01-05  1663.36  2024286  3373155600  1661.33  1678.66  1652.11
4   2024-01-08  1643.99  2558620  4211918600  1661.00  1662.00  1640.01
..         ...      ...      ...         ...      ...      ...      ...
307 2025-04-14  1551.99  2171144  3379425600  1560.97  1566.00  1551.53
308 2025-04-15  1558.00  2148928  3339942700  1552.00  1565.00  1545.00
309 2025-04-16  1559.17  3115605  4834880600  1552.00  1576.00  1537.00
310 2025-04-17  1570.00  2384605  3733925000  1554.00  1576.50  1549.99
311 2025-04-18  1565.94  2029848  3179974300  1566.00  1575.00  1556.00

[312 rows x 7 columns]
```

```python
from thsdk import THS
import pandas as pd

with THS() as ths:
    response = ths.wencai_nlp("涨停;所属概念")
    print(pd.DataFrame(response.payload.data))



```

### Result:

```
                                                 所属概念    最新价  ...       股票代码   股票简称
0   智慧城市;数字经济;MiniLED;东数西算(算力);卫星导航;PCB概念;军工;华为概念;...   6.69  ...  002848.SZ  *ST高斯
1                    股权转让(并购重组);ST板块;数据要素;智慧城市;传感器;风电   6.41  ...  600421.SH  *ST华嵘
2   露营经济;体育产业;跨境电商;电子商务;旅游概念;参股银行;共同富裕示范区;长三角一体化;C...   4.07  ...  002489.SZ   浙江永强
3   C2M概念;电子商务;跨境电商;参股银行;工业大麻;国企改革;人民币贬值受益;回购增持再贷款...   5.28  ...  600448.SH   华纺股份
4          特色小镇;物业管理;租售同权;雄安新区;PPP概念;国企改革;央企国企改革;ST板块   1.83  ...  002305.SZ  *ST南置
5   可降解塑料;无线充电;军工信息化;两轮车;储能;军工;光伏概念;富士康概念;低空经济;医疗器...  11.72  ...  002735.SZ   王子新材
```

```python
# 使用非with用法完整版本
from thsdk import THS
import pandas as pd


def main():
    # 初始化
    ths = THS()

    try:
        # 连接到行情服务器
        response = ths.connect()
        if response.errInfo != "":
            print(f"登录错误:{response.errInfo}")
            return
        else:
            print("Connected to the server.")

        # 获取历史日级别数据
        response = ths.get_block_data(0xCE5F)
        if response.errInfo != "":
            print(f"查询错误:{response.errInfo}")
            return

        df = pd.DataFrame(response.payload.data)
        print(df)

        print("查询成功 数量:", len(response.payload.data))

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # 断开连接
        ths.disconnect()
        print("Disconnected from the server.")


if __name__ == "__main__":
    main()

```

### Result:

```
Connected to the server.
          code   name
0   URFI881165     综合
1   URFI881171  自动化设备
2   URFI881118   专用设备
3   URFI881141     中药
4   URFI881157     证券
..         ...    ...
85  URFI881138   包装印刷
86  URFI881121    半导体
87  URFI881131   白色家电
88  URFI881273     白酒
89  URFI881271   IT服务

[90 rows x 2 columns]
查询成功 数量: 90
Disconnected from the server.
```

```python
from thsdk import THS

with THS() as ths:
    print(ths.help("about"))
```

### examples.py

```python

from thsdk import THS
import pandas as pd


def main():
    # 初始化 THS 实例
    with THS() as ths:
        # 示例 1: 查询历史近 100 条日 K 数据
        response = ths.download("USHA600519", count=100)
        print("历史近 100 条日 K 数据:")
        print(pd.DataFrame(response.payload.data))

        # 示例 2: 查询市场板块数据
        response = ths.get_block_data(0xE)
        print("市场板块数据:")
        print(pd.DataFrame(response.payload.data))

        # 示例 3: 查询股票市场数据
        df = pd.DataFrame(response.payload.data)
        usza_codes = df[df['代码'].str.startswith('USZA')]['代码'].tolist()
        response = ths.stock_market_data(usza_codes)
        print("股票市场数据:")
        print(pd.DataFrame(response.payload.data))


if __name__ == "__main__":
    main()

```