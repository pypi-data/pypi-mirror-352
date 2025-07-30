# encoding: utf-8
# -----------------------------------------#
# Filename:     thsdk.py
#
# Description:  同花顺金融数据 API，用于获取市场行情数据（如 K 线、成交、板块等）。
# Version:      2.0
# Created:      2018/2/30 15:46
# Author:       panghu11033@gmail.com
#
# -----------------------------------------#

import os
import re
import json
import time
import random
import logging
import datetime
import platform
import ctypes as c
from ctypes import CFUNCTYPE
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional
from ._guest import rand_account

__all__ = ['THS', 'Adjust', 'Interval', 'Response', 'Payload', 'HQ']

tz = ZoneInfo('Asia/Shanghai')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)
logger = logging.getLogger(__name__)


def _int2time(scr: int) -> datetime.datetime:
    """将整数时间戳转换为 datetime 对象。

    Args:
        scr (int): 整数时间戳，包含年、月、日、小时、分钟信息。

    Returns:
        datetime.datetime: 转换后的 datetime 对象，带亚洲/上海时区。

    Raises:
        ValueError: 如果时间戳无效。
    """
    try:
        year = 2000 + ((scr & 133169152) >> 20) % 100
        month = (scr & 983040) >> 16
        day = (scr & 63488) >> 11
        hour = (scr & 1984) >> 6
        minute = scr & 63
        return datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
    except ValueError as e:
        raise ValueError(f"无效的时间整数: {scr}, 错误: {e}")


def _is_valid_time(time_value: int) -> bool:
    """检查时间戳是否有效。

    Args:
        time_value (int): 要检查的整数时间戳。

    Returns:
        bool: 如果时间戳有效，返回 True，否则返回 False。
    """
    try:
        _int2time(time_value)
        return True
    except ValueError:
        return False


def _time2int(t: datetime) -> int:
    """将 datetime 对象转换为整数时间戳。

    Args:
        t (datetime): datetime 对象，可能不带时区信息。

    Returns:
        int: 转换后的整数时间戳。

    Notes:
        如果输入的 datetime 对象不带时区，将自动设置为亚洲/上海时区。
    """
    if not t.tzinfo:
        t = t.replace(tzinfo=tz)
    return (t.minute + (t.hour << 6) + (t.day << 11) +
            (t.month << 16) + (t.year << 20)) - 0x76c00000


def _convert_data_keys(data: List[Dict]) -> List[Dict]:
    """转换数据字段名称为中文。

    Args:
        data (List[Dict]): 包含字段名称的字典列表。

    Returns:
        List[Dict]: 字段名称转换为中文后的字典列表。
    """
    converted_data = []
    for entry in data:
        converted_entry = {}
        for key, value in entry.items():
            key_int = int(key) if key.isdigit() else key
            converted_entry[FieldNameMap.get(key_int, key)] = value
        converted_data.append(converted_entry)
    return converted_data


def _market_code2str(market_code: str) -> str:
    """将市场代码转换为字符串表示。

    Args:
        market_code (str): 市场代码，如 "17" 表示上海A股。

    Returns:
        str: 市场字符串表示，如 "USHA"。
    """
    market_map = {
        "17": "USHA",  # 上海A股
        "22": "USHT",  # 上海退市整理
        "33": "USZA",  # 深圳A股
        "37": "USZP",  # 深圳退市整理
        "49": "URFI",  # 指数
        "151": "USTM",  # 北交所
    }
    return market_map.get(market_code, "")


def _market_str(market_code: str) -> str:
    """获取市场字符串表示，处理异常情况。

    Args:
        market_code (str): 市场代码。

    Returns:
        str: 市场字符串表示，若代码无效返回空字符串。

    Notes:
        若市场代码未知，将记录警告日志。
    """
    try:
        return _market_code2str(market_code)
    except ValueError:
        logger.warning(f"未知的市场代码: {market_code}")
        return ""


# 市场代码列表
MARKETS = ['USHI', 'USHA', 'USHB', 'USHD', 'USHJ', 'USHP', 'USHT', 'USZI', 'USZA', 'USZB', 'USZD', 'USZJ',
           'USZP', 'USOO', 'UZOO']

BLOCK_MARKETS = ['URFI']


class Adjust:
    """K 线复权类型定义。

    Attributes:
        FORWARD (str): 前复权。
        BACKWARD (str): 后复权。
        NONE (str): 不复权。
    """
    FORWARD = "Q"
    BACKWARD = "B"
    NONE = ""

    @classmethod
    def all_types(cls) -> List[str]:
        """获取所有复权类型。

        Returns:
            List[str]: 包含所有复权类型的列表。
        """
        return [cls.FORWARD, cls.BACKWARD, cls.NONE]


class Interval:
    """K 线周期类型定义。

    Attributes:
        MIN_1 (int): 1 分钟 K 线。
        MIN_5 (int): 5 分钟 K 线。
        MIN_15 (int): 15 分钟 K 线。
        MIN_30 (int): 30 分钟 K 线。
        MIN_60 (int): 60 分钟 K 线。
        MIN_120 (int): 120 分钟 K 线。
        DAY (int): 日 K 线。
        WEEK (int): 周 K 线。
        MONTH (int): 月 K 线。
        QUARTER (int): 季 K 线。
        YEAR (int): 年 K 线。
    """
    MIN_1 = 0x3001
    MIN_5 = 0x3005
    MIN_15 = 0x300f
    MIN_30 = 0x301e
    MIN_60 = 0x303c
    MIN_120 = 0x3078
    DAY = 0x4000
    WEEK = 0x5001
    MONTH = 0x6001
    QUARTER = 0x6003
    YEAR = 0x7001

    @classmethod
    def minute_intervals(cls) -> List[int]:
        """获取分钟级别周期。

        Returns:
            List[int]: 包含分钟级别周期的列表。
        """
        return [cls.MIN_1, cls.MIN_5, cls.MIN_15, cls.MIN_30, cls.MIN_60, cls.MIN_120]

    @classmethod
    def day_and_above_intervals(cls) -> List[int]:
        """获取日及以上级别周期。

        Returns:
            List[int]: 包含日及以上级别周期的列表。
        """
        return [cls.DAY, cls.WEEK, cls.MONTH, cls.QUARTER, cls.YEAR]

    @classmethod
    def all_types(cls) -> List[int]:
        """获取所有周期类型。

        Returns:
            List[int]: 包含所有周期类型的列表。
        """
        return cls.minute_intervals() + cls.day_and_above_intervals()


# 订阅数据类型：1-指数快照，2-证券快照，3-委托队列，4-逐笔委托，5-逐笔成交，5-极速盘口
DATA_CLASS_LIST = [1, 2, 3, 4, 5, 6]
DATA_CLASS_NAMES = ['index', 'stock', 'queue', 'order', 'trans', 'superstock']
# 数据类型：0xf-数据类型，0x0-交易所原始数据，0x1-使用压缩，0xf0-数据类型，0x10-更新补全后的数据
DATA_OP_TYPE = [0xf, 0x0, 0x1, 0xf0, 0x10]
# 订阅操作类型：1-全新订阅，2-取消订阅，3-该市场增加订阅代码，4-该市场删除订阅代码
SUB_OP_TYPE = [1, 2, 3, 4]

# 市场代码
MarketUSHI = "USHI"  # 上海指数
MarketUSHA = "USHA"  # 上海A股
MarketUSHB = "USHB"  # 上海B股
MarketUSHD = "USHD"  # 上海债券
MarketUSHJ = "USHJ"  # 上海基金
MarketUSHP = "USHP"  # 上海退市整理
MarketUSHT = "USHT"  # 上海ST风险警示板
MarketUSZI = "USZI"  # 深圳指数
MarketUSZA = "USZA"  # 深圳A股
MarketUSZB = "USZB"  # 深圳B股
MarketUSZD = "USZD"  # 深圳债券
MarketUSZJ = "USZJ"  # 深圳基金
MarketUSZP = "USZP"  # 深圳退市整理
MarketUSTM = "USTM"  # 北交所

# 字段名称映射（已修正重复值问题）
FieldNameMap = {
    1: "时间",
    5: "代码",
    6: "昨收价",
    7: "开盘价",
    8: "最高价",
    9: "最低价",
    10: "价格",
    11: "收盘价",
    12: "成交方向",
    13: "成交量",
    14: "外盘成交量",
    15: "内盘成交量",
    16: "对倒成交量",
    17: "开盘成交量",
    18: "交易笔数",
    19: "总金额",
    20: "委托买入价",
    21: "委托卖出价",
    22: "委买总量",
    23: "委卖总量",
    24: "买1价",
    25: "买1量",
    26: "买2价",
    27: "买2量",
    28: "买3价",
    29: "买3量",
    30: "卖1价",
    31: "卖1量",
    32: "卖2价",
    33: "卖2量",
    34: "卖3价",
    35: "卖3量",
    36: "指数种类",
    37: "股票总数",
    38: "上涨家数",
    39: "下跌家数",
    40: "领先指标",
    41: "上涨趋势",
    42: "下跌趋势",
    43: "最近成交金额",
    44: "证券名称(繁体)",
    45: "五日成交总量",
    46: "证券名称(英文)",
    47: "证券名称(Unicode)",
    48: "涨速",
    49: "当前量(手)",
    50: "代码(港)",
    53: "委比",
    54: "均价(中金所)",
    55: "名称",
    56: "挂单时间",
    60: "H股昨收",
    61: "异动类型1",
    64: "状态",
    65: "持仓",
    66: "昨结",
    69: "涨停价",
    70: "跌停价",
    71: "现增仓",
    72: "今结",
    73: "昨持仓",
    74: "买单ID",
    75: "卖单ID",
    80: "利息",
    82: "撤单时间",
    84: "所属行业",
    85: "盈利情况",
    89: "转让状态参数",
    90: "板块流通市值",
    91: "市盈率",
    92: "板块总市值",
    93: "交易单位",
    95: "52周最高",
    96: "52周最低",
    100: "现价(港)",
    102: "买6价",
    103: "买6量",
    104: "卖6价",
    105: "卖6量",
    106: "买7价",
    107: "买7量",
    108: "卖7价",
    109: "卖7量",
    110: "买8价",
    111: "买8量",
    112: "卖8价",
    113: "卖8量",
    114: "买9价",
    115: "买9量",
    116: "卖9价",
    117: "卖9量",
    118: "买10价",
    119: "买10量",
    120: "卖10价",
    121: "卖10量",
    122: "加权平均买价",
    123: "总委买量",
    124: "加权平均卖价",
    125: "总委卖量",
    130: "总手(港)",
    141: "波动性中断参考价",
    142: "波动性中断虚拟匹配量",
    143: "合约代码",
    144: "标的证券代码",
    145: "标的证券名称",
    146: "标的证券类型",
    147: "期权类型",
    148: "认购认沽",
    149: "合约单位",
    150: "买4价",
    151: "买4量",
    152: "卖4价",
    153: "卖4量",
    154: "买5价",
    155: "买5量",
    156: "卖5价",
    157: "卖5量",
    160: "市场分层",
    191: "买差价",
    192: "卖差价",
    201: "主动买入特大单量",
    202: "主动卖出特大单量",
    203: "主动买入大单量",
    204: "主动卖出大单量",
    205: "主动买入中单量",
    206: "主动卖出中单量",
    207: "被动买入特大单量",
    208: "被动卖出特大单量",
    209: "被动买入大单量",
    210: "被动卖出大单量",
    211: "被动买入中单量",
    212: "被动卖出中单量",
    213: "主动买入小单量",
    214: "主动卖出小单量",
    215: "主动买入特大单笔数",
    216: "主动卖出特大单笔数",
    217: "主动买入大单笔数",
    218: "主动卖出大单笔数",
    219: "被动买入特大单笔数",
    220: "被动卖出特大单笔数",
    221: "被动买入大单笔数",
    222: "被动卖出大单笔数",
    223: "主动买入特大单金额",
    224: "主动卖出特大单金额",
    225: "主动买入大单金额",
    226: "主动卖出大单金额",
    227: "被动买入特大单金额",
    228: "被动卖出特大单金额",
    229: "被动买入大单金额",
    230: "被动卖出大单金额",
    231: "买入单数量",
    232: "卖出单数量",
    233: "资金流入",
    234: "资金流出",
    235: "大单净量正",
    236: "大单净量负",
    237: "主动买入小单金额",
    238: "主动卖出小单金额",
    239: "成交笔数",
    240: "昨日收盘收益率",
    241: "昨日加权平均收益率",
    242: "开盘收益率",
    243: "最高收益率",
    244: "最低收益率",
    245: "最新收益率",
    246: "当日加权平均收益率",
    250: "委托买入前五档金额",
    251: "委托卖出前五档金额",
    252: "委托买入前十档金额",
    253: "委托卖出前十档金额",
    255: "主动买入中单笔数",
    256: "主动卖出中单笔数",
    257: "被动买入中单笔数",
    258: "被动卖出中单笔数",
    259: "主动买入中单金额",
    260: "主动卖出中单金额",
    261: "被动买入中单金额",
    262: "被动卖出中单金额",
    271: "52周最高日期",
    272: "52周最低日期",
    273: "年度最高日期",
    274: "年度最低日期",
    275: "领涨股",
    276: "涨停家数",
    277: "跌停家数",
    278: "盘后最新价",
    279: "港股指数人民币成交金额",
    280: "期权行权价",
    281: "首个交易日",
    282: "最后交易日1",
    283: "期权行权日",
    284: "期权到期日",
    285: "合约版本号",
    286: "行权交割日",
    288: "标的证券前收盘",
    289: "涨跌幅限制类型",
    290: "保证金比例参数1",
    291: "保证金比例参数2",
    292: "单位保证金",
    294: "整手数",
    295: "单笔限价申报下限",
    296: "单笔限价申报上限",
    297: "单笔市价申报下限",
    298: "单笔市价申报上限",
    299: "期权合约状态标签",
    402: "总股本",
    407: "流通股本",
    410: "流通B股",
    471: "权息资料",
    497: "转股价",
    499: "债券余额",
    520: "流动资产",
    543: "资产总计",
    593: "公积金",
    602: "主营收入",
    605: "营业利润",
    615: "利润总额",
    619: "净利润1",
    672: "申购限额(万股)",
    675: "实际涨幅",
    676: "首日振幅",
    873: "引伸波幅",
    874: "对冲值",
    875: "街货占比",
    876: "街货量",
    877: "最后交易日2",
    879: "回收价",
    880: "牛熊证种类",
    881: "标的证券",
    882: "权证类型",
    887: "行使价",
    888: "换股比率1",
    890: "到期日",
    899: "财务数据项",
    900: "流通股变动量",
    981: "港元人民币汇率",
    1002: "每股收益",
    1005: "每股净资产",
    1015: "净资产收益率",
    1024: "债券规模",
    1047: "转股起始日",
    1110: "星级",
    1121: "标记",
    1322: "利率",
    1384: "融资余额",
    1385: "融券余额",
    1386: "融资买入",
    1387: "融券卖出",
    1566: "净利润2",
    1606: "发行价",
    1612: "中签率",
    1670: "股东总数",
    1674: "流通A股",
    2026: "评级",
    2039: "纯债价值",
    2041: "期权价值",
    2570: "卖出信号",
    2579: "机构持股比例",
    2719: "人均持股数",
    2942: "市盈率(动态)1",
    2946: "市盈率(静态)",
    2947: "市净率1",
    3153: "市盈率TTM",
    3250: "5日涨幅",
    3251: "10日涨幅",
    3252: "20日涨幅",
    3397: "净值",
    9810: "溢价率",
    32772: "时间戳",
    68107: "板块主力净量1",
    68166: "板块主力流入",
    68167: "板块主力流出",
    68213: "板块主力净流入",
    68285: "板块主力净量2",
    68759: "板块开盘价",
    133702: "细分行业",
    133778: "基差",
    133964: "日增仓1",
    134071: "市销率TTM",
    134072: "净资产收益率TTM",
    134141: "净利润增长率",
    134143: "营业收入增长率",
    134152: "市盈率(静态)2",
    134160: "换股比率2",
    134162: "折溢率",
    134237: "杠杆比率",
    134238: "溢价",
    199112: "涨幅",
    199643: "大单净量",
    264648: "涨跌",
    330321: "异动类型2",
    330322: "竞价评级1",
    330325: "涨停类型",
    330329: "涨停状态",
    331070: "今日主力增仓占比",
    331077: "2日主力增仓占比",
    331078: "3日主力增仓占比",
    331079: "5日主力增仓占比",
    331080: "10日主力增仓占比",
    331124: "2日主力增仓排名",
    331125: "3日主力增仓排名",
    331126: "5日主力增仓排名",
    331127: "10日主力增仓排名",
    331128: "今日主力增仓排名",
    395720: "委差",
    461256: "委比",
    461346: "年初至今涨幅",
    461438: "涨速(10分钟)",
    461439: "涨速(15分钟)",
    462057: "散户数量",
    526792: "振幅",
    527198: "未知字段527198",
    527526: "涨速(3分钟)",
    527527: "涨速(1分钟)",
    592544: "贡献度",
    592920: "市净率2",
    592741: "机构动向",
    592888: "主力净量",
    592890: "主力净流入",
    592893: "5日大单净量",
    592894: "10日大单净量",
    592946: "多空比",
    625362: "每股公积金",
    625295: "成交笔数2",
    658784: "金叉个数",
    658785: "利好",
    658786: "利空",
    920371: "开盘涨幅",
    920372: "实体涨幅",
    920428: "股票分类标记",
    1149395: "市净率3",
    1378761: "均价",
    1509847: "户均持股数",
    1640904: "手每笔",
    1771976: "量比",
    1968584: "换手率",
    1991120: "涨幅(港)",
    2034120: "市盈率(动态)2",
    2034121: "资产负债率",
    2097453: "流通股",
    2263506: "流通比例",
    2427336: "均笔额",
    2646480: "H股涨跌",
    2820564: "内盘",
    3082712: "涨幅(结算)",
    3475914: "流通市值",
    3541450: "总市值",
    3934664: "板块涨速",
    4065737: "买价",
    4099083: "日增仓2",
    4131273: "卖价",
    4525375: "小单流入",
    4525376: "中单流入",
    4525377: "大单流入",
    7000001: "占基金规模1",
    7000002: "持股变动1",
    7000003: "基金规模1",
    7000004: "代码2",
    7000005: "涨幅百分比",
    7000006: "持股变动2",
    7000007: "占基金规模2",
    7000008: "业绩表现",
    7000009: "近一年收益",
    7000010: "近一周收益",
    7000011: "近一月收益",
    7000012: "近三月收益",
    7000013: "今年以来收益",
    7000014: "成立以来收益",
    7000015: "产品类型",
    7000016: "基金规模2",
    7000017: "基金公司",
    7000018: "投资类型",
    7000019: "基金经理",
    7000020: "资产占比",
    7000021: "较上期",
    8311855: "类别",
    8719679: "小单流出",
    8719680: "中单流出",
    8719681: "大单流出",
    12345671: "A股关联主题",
    12913983: "小单净额",
    12913984: "中单净额",
    12913985: "大单净额",
    17108287: "小单净额占比",
    17108288: "中单净额占比",
    17108289: "大单净额占比",
    18550831: "成分股数",
    20190901: "标签",
    21302591: "小单总额",
    21302592: "中单总额",
    21302593: "大单总额",
    25496895: "小单总额占比",
    25496896: "中单总额占比",
    25496897: "大单总额占比",
    189546735: "计算数据项",
    2018090319: "竞价评级2",
    2018090320: "竞价异动说明",
    2018090410: "异动说明",
    2018090411: "竞价涨幅",
}


class THSAPIError(Exception):
    """同花顺 API 异常基类。"""
    pass


class NoDataError(THSAPIError):
    """服务器未返回数据时抛出。"""
    pass


class InvalidCodeError(THSAPIError):
    """无效证券代码时抛出。"""
    pass


class InvalidDateError(THSAPIError):
    """无效日期格式时抛出。"""
    pass


class HQ:
    """行情服务核心类，负责与 C 动态链接库交互，提供连接、查询、订阅等功能。

    该类通过调用 C 动态链接库的 DataAccess 函数实现行情服务操作，包括连接、断开连接、查询数据、订阅和取消订阅。
    所有方法返回 tuple[int, str]，其中状态码 0 表示成功，其他负值表示错误，具体如下：
        - 0: 成功
        - -1: 输出缓冲区太小
        - -2: 输入参数无效
        - -3: 内部错误或连接失败
        - -4: 查询失败
        - -5: 未连接到服务器
    返回的字符串为 JSON 格式的响应，成功时包含数据，失败时包含错误信息。
    该类是线程安全的，底层库使用互斥锁确保并发调用安全。
    """

    def __init__(self, ops: Dict[str, Any] = None):
        """初始化行情服务。

        Args:
            ops (Dict[str, Any], optional): 配置字典，包含连接所需的用户名和密码等信息。默认为 None。

        Raises:
            THSAPIError: 如果动态链接库加载失败或操作系统不受支持。
        """
        self.ops = ops or {}
        self.__lib_path = self._get_lib_path()
        self._lib = None
        self._callbacks = []
        self._initialize_library()

    def _get_lib_path(self) -> str:
        """获取动态链接库路径。

        Returns:
            str: 动态链接库的路径。

        Raises:
            THSAPIError: 如果操作系统或架构不受支持。
        """
        system = platform.system()
        arch = platform.machine()
        base_dir = os.path.dirname(__file__)
        if system == 'Linux':
            return os.path.join(base_dir, "hq.so")
        elif system == 'Darwin':
            if arch == 'arm64':
                raise THSAPIError('Apple M系列芯片暂不支持')
            return os.path.join(base_dir, 'hq.dylib')
        elif system == 'Windows':
            return os.path.join(base_dir, 'hq.dll')
        raise THSAPIError(f'不支持的操作系统: {system}')

    def _initialize_library(self) -> None:
        """初始化 C 动态链接库。

        Raises:
            THSAPIError: 如果加载动态链接库失败。
        """
        try:
            self._lib = c.CDLL(self.__lib_path)
            self._lib.DataAccess.argtypes = [c.c_char_p, c.c_char_p, c.c_int, c.c_void_p]
            self._lib.DataAccess.restype = c.c_int
        except OSError as e:
            raise THSAPIError(f"加载动态链接库 {self.__lib_path} 失败: {e}")

    def call_data_access(self, operation: str, req: str = "", service_type: str = "",
                         buffer_size: int = 1024 * 1024, callback: Optional[CFUNCTYPE] = None) -> tuple[int, str]:
        """调用 C 动态链接库的 DataAccess 函数，处理所有行情服务操作。
        内部方法，统一调用 C 动态链接库的 DataAccess 函数，处理所有行情服务操作。

        该方法封装了对 C 动态链接库的调用，负责构造输入 JSON，分配输出缓冲区，调用 DataAccess 函数，
        并解析返回结果。支持的操作包括连接、断开连接、查询数据、订阅和取消订阅等。

        Args:
            operation: 操作类型，可选值：
                - "connect": 连接行情服务器
                - "disconnect": 断开行情服务器连接
                - "query_data": 查询行情数据
                - "subscribe": 订阅实时行情数据
                - "unsubscribe": 取消订阅
                - "help": 获取帮助信息
            req: 请求字符串，具体内容取决于操作类型：
                - connect: 账户信息配置字典序列化为 JSON
                - unsubscribe: 订阅 ID（字符串格式）
                - query_data/subscribe/help: 自定义请求字符串
                - disconnect: 忽略
            service_type: 服务类型，仅对 query_data 和 subscribe 操作有效，可选值包括：
                - "zhu": 主行情服务
                - "fu": 副行情服务
                - "zx": 资讯行情服务
                - "bk": 板块行情服务
                - "wencai_base": 问财基础服务
                - "wencai_nlp": 问财自然语言处理服务
                - "order_book_bid": 市场深度买20档
                - "order_book_ask": 市场深度卖20档
                - "ipo_today": 今日申购IPO
                - "ipo_wait": 等待排队IPO
                - "push": 实时推送服务（用于 subscribe）
                - "": 其他操作使用空字符串
            callback: 回调函数，仅对 subscribe 操作有效，用于接收实时推送数据。
                      签名必须为 CFUNCTYPE(None, c_char_p)，接收 UTF-8 编码的 JSON 字符串。
            buffer_size: 输出缓冲区大小（字节），默认为 1MB，需足够大以容纳返回数据。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            THSAPIError: 如果调用 DataAccess 失败、输出缓冲区解码失败或 JSON 序列化/反序列化错误。
        """
        input_json = {
            "operation": operation,
            "service_type": service_type,
            "request": json.dumps(self.ops) if operation == "connect" else req
        }

        input_json_bytes = json.dumps(input_json).encode('utf-8')
        output_buffer = c.create_string_buffer(buffer_size)
        current_buffer_size = buffer_size

        status = self._lib.DataAccess(input_json_bytes, output_buffer, c.c_int(current_buffer_size), callback)
        try:
            result = output_buffer.value.decode('utf-8') if output_buffer.value else ""
        except UnicodeDecodeError:
            raise THSAPIError("[thsdk] 输出缓冲区解码失败，可能包含非 UTF-8 数据")

        return status, result

    def connect(self, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """连接行情服务器。

        Args:
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            THSAPIError: 如果连接失败。
        """
        return self.call_data_access("connect", req=json.dumps(self.ops), buffer_size=buffer_size)

    def disconnect(self, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """断开行情服务器连接。

        Args:
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            THSAPIError: 如果断开连接失败。
        """
        return self.call_data_access("disconnect", buffer_size=buffer_size)

    def query_data(self, req: str, service_type: str, buffer_size: int = 1024 * 1024 * 2) -> tuple[int, str]:
        """查询行情数据。

        Args:
            req (str): 查询请求字符串，如 "id=202&instance=2384376321&zipversion=2&codelist=301024&market=USZA"。
            service_type (str): 服务类型，如 "zhu", "fu", "bk", "wencai_base", "ipo_today"。
                - zhu: 主行情服务
                - fu: 副行情服务
                - zx: 资讯行情服务
                - bk: 板块行情服务
                - wencai_base: 问财基础服务
                - wencai_nlp: 问财自然语言处理服务
                - order_book_bid: 市场深度买20档
                - order_book_ask: 市场深度卖20档
                - ipo_today: 今日申购IPO
                - ipo_wait: 等待排队IPO
                - help: 帮助服务（req 可为 "version", "about", "doc", "donation"）
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            THSAPIError: 如果查询失败。
        """
        return self.call_data_access("query_data", req=req, service_type=service_type, buffer_size=buffer_size)

    def subscribe(self, req: str = "", service_type: str = "push", buffer_size: int = 1024 * 1024,
                  callback: CFUNCTYPE = None) -> tuple[int, str]:
        """订阅实时行情数据。

        Args:
            req (str, optional): 订阅请求字符串，如 "1" 表示实时价格更新。默认为空字符串。
            service_type (str, optional): 服务类型，当前仅支持 "push"。默认为 "push"。
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。
            callback (CFUNCTYPE, optional): 回调函数，需为 CFUNCTYPE(None, c_char_p) 类型。

        Returns:
            tuple[int, str]: 包含订阅 ID 和返回数据的元组。订阅 ID 为正整数表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            ValueError: 如果 callback 不是有效的 CFUNCTYPE 类型。
            THSAPIError: 如果订阅失败。
        """
        if not isinstance(callback, CFUNCTYPE(None, c.c_char_p)):
            raise ValueError("回调函数必须为 ctypes.CFUNCTYPE 类型，签名需为 CFUNCTYPE(None, c_char_p)")
        self._callbacks.append(callback)
        return self.call_data_access("subscribe", req=req, service_type=service_type, buffer_size=buffer_size,
                                     callback=callback)

    def unsubscribe(self, subscription_id: str, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """取消订阅实时行情数据。

        Args:
            subscription_id (str): 订阅 ID，由 subscribe 方法返回。
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。

        Raises:
            THSAPIError: 如果取消订阅失败。
        """
        return self.call_data_access("unsubscribe", req=str(subscription_id), buffer_size=buffer_size)

    def help(self, req: str = "", buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """获取帮助信息。

        Args:
            req (str, optional): 查询条件，如 "about"。默认为空字符串。
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: 包含状态码和返回数据的元组。状态码为 0 表示成功，负值表示错误；返回数据为 JSON 格式字符串。
        """
        return self.call_data_access("help", req=req, service_type="", buffer_size=buffer_size)


class Payload:
    """API 响应数据类，用于存储和处理返回的数据。

    Attributes:
        type (str): 数据类型。
        data (List[Dict]): 数据列表，每个元素为字段字典。
        dic_extra (Dict[str, Any]): 额外信息字典。
        extra (Any): 其他额外数据。
        subscribe_id (str): 订阅 ID。
        help (str): 帮助信息。
    """

    def __init__(self, data_dict: Dict[str, Any]):
        """初始化响应数据。

        Args:
            data_dict (Dict[str, Any]): 包含响应数据的字典。
        """
        self.type: str = data_dict.get('type', "")
        self.data: List[Dict] = data_dict.get('data', [])
        self.dic_extra: Dict[str, Any] = data_dict.get('dic_extra', {})
        self.extra: Any = data_dict.get('extra', None)
        self.subscribe_id: str = data_dict.get('subscribe_id', "")
        self.help: str = data_dict.get('help', "")

    def __repr__(self) -> str:
        """返回对象的字符串表示。

        Returns:
            str: 对象的简洁字符串表示，包含主要属性信息。
        """
        data_preview = self.data[:2] if len(self.data) > 2 else self.data
        return (f"Payload(type={self.type!r}, "
                f"data={data_preview!r}... ({len(self.data)} items), "
                f"dic_extra={self.dic_extra!r}, extra={self.extra!r}, "
                f"subscribe_id={self.subscribe_id!r}, help={self.help!r})")

    def is_empty(self) -> bool:
        """检查数据是否为空。

        Returns:
            bool: 如果数据为空返回 True，否则返回 False。
        """
        return not bool(self.data)

    def get_extra_value(self, key: str, default: Any = None) -> Any:
        """从额外信息中获取值。

        Args:
            key (str): 要获取的键。
            default (Any, optional): 默认值，若键不存在返回该值。默认为 None。

        Returns:
            Any: 键对应的值，或默认值。
        """
        return self.dic_extra.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典。

        Returns:
            Dict[str, Any]: 包含对象所有属性的字典。
        """
        return {
            "type": self.type,
            "data": self.data,
            "dic_extra": self.dic_extra,
            "extra": self.extra,
            "subscribe_id": self.subscribe_id,
            "help": self.help
        }


class Response:
    """API 响应类，用于解析和处理 API 返回的 JSON 数据。

    Attributes:
        errInfo (str): 错误信息，若为空表示成功。
        payload (Payload): 响应数据对象。
    """

    def __init__(self, json_str: str):
        """初始化响应对象。

        Args:
            json_str (str): JSON 格式的响应字符串。

        Notes:
            如果 JSON 字符串无效，将记录错误并初始化为空数据。
        """
        try:
            data_dict: Dict[str, Any] = json.loads(json_str)
        except json.JSONDecodeError as e:
            data_dict: Dict[str, Any] = {}
            print(f"无效的 JSON 字符串: {e}")

        self.errInfo: str = data_dict.get("errInfo", "")
        self.payload: Payload = Payload(data_dict.get("payload", {}))

    def __repr__(self) -> str:
        """返回对象的字符串表示。

        Returns:
            str: 包含错误信息和数据对象的字符串表示。
        """
        return f"Response(errInfo={self.errInfo}, payload={self.payload})"

    def convert_data(self) -> None:
        """转换数据字段名称为中文。

        Notes:
            调用 _convert_data_keys 函数处理 payload.data 中的字段名称。
        """
        self.payload.data = _convert_data_keys(self.payload.data or [])

    def is_success(self) -> bool:
        """检查响应是否成功。

        Returns:
            bool: 如果 errInfo 为空返回 True，否则返回 False。
        """
        return self.errInfo == ""

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典。

        Returns:
            Dict[str, Any]: 包含错误信息和数据对象的字典。
        """
        return {
            "errInfo": self.errInfo,
            "payload": self.payload.to_dict() if self.payload else None,
        }


def error_response(err_info: str) -> Response:
    """创建错误响应对象。

    Args:
        err_info (str): 错误信息字符串。

    Returns:
        Response: 包含错误信息和空 payload 的响应对象。
    """
    return Response(json.dumps({
        "errInfo": err_info,
        "payload": {}
    }))


class THS:
    """同花顺金融数据 API 客户端，提供行情数据查询和订阅功能。

    该类封装了与行情服务器的交互，支持获取 K 线、成交、板块等数据，以及实时数据订阅。
    """

    def __init__(self, ops: Optional[Dict[str, Any]] = None):
        """初始化 API 客户端。

        Args:
            ops (Dict[str, Any], optional): 配置信息，包含用户名、密码等。默认为 None，若未提供则使用随机账户。
        """
        ops = ops or {}
        account = rand_account()
        ops.setdefault("username", account[0])
        ops.setdefault("password", account[1])
        self.ops = ops
        self._hq = HQ(ops)
        self._login = False
        self.__share_instance = random.randint(6666666, 8888888)

    def __enter__(self):
        """上下文管理器入口，自动连接服务器。

        Returns:
            THS: 客户端对象自身。
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动断开服务器连接。"""
        self.disconnect()

    @property
    def zip_version(self) -> int:
        """获取压缩版本号。

        Returns:
            int: 当前压缩版本号，固定为 2。
        """
        return 2

    @property
    def share_instance(self) -> int:
        """获取共享实例 ID。

        Returns:
            int: 自增的共享实例 ID。
        """
        self.__share_instance += 1
        return self.__share_instance

    def connect(self, max_retries: int = 5) -> Response:
        """连接到行情服务器。

        Args:
            max_retries (int, optional): 最大重试次数，默认为 5。

        Returns:
            Response: 包含连接结果的响应对象。

        Raises:
            ValueError: 如果 max_retries 小于或等于 0。
        """
        if not isinstance(max_retries, int) or max_retries <= 0:
            max_retries = 5

        for attempt in range(max_retries):
            try:
                buffer_size = 1024 * 10
                result_code, result = self._hq.connect(buffer_size)
                if result_code != 0:
                    logger.error(f"❌ 错误代码: {result_code}, 连接失败")
                    return error_response(f"错误代码: {result_code}, 连接失败")
                response = Response(result)

                if response.errInfo == "":
                    self._login = True
                    logger.info("✅ 成功连接到服务器")
                    return response
                else:
                    logger.warning(f"❌ 第 {attempt + 1} 次连接尝试失败: {response.errInfo}")
            except Exception as e:
                logger.error(f"❌ 连接报错: {e}")
            time.sleep(2 ** attempt)
        logger.error(f"❌ 尝试 {max_retries} 次后连接失败")
        return error_response(f"尝试 {max_retries} 次后连接失败")

    def disconnect(self):
        """断开与行情服务器的连接。

        Notes:
            如果未连接，则记录已断开信息。
        """
        if self._login:
            self._login = False
            self._hq.disconnect()
            logger.info("✅ 已成功断开与行情服务器的连接")
        else:
            logger.info("✅ 已经断开连接")

    def query_data(self, req: str, service_type: str = "zhu", buffer_size: int = 1024 * 1024 * 2,
                   max_attempts=5) -> Response:
        """查询行情数据。

        Args:
            req (str): 查询请求字符串。
            service_type (str, optional): 查询类型，默认为 "zhu"。
            buffer_size (int, optional): 输出缓冲区大小（字节），默认为 2MB。
            max_attempts (int, optional): 最大尝试次数，默认为 5。

        Returns:
            Response: 包含查询结果的响应对象。

        Notes:
            如果未登录，返回未授权响应。
            如果缓冲区不足，会自动扩大缓冲区并重试。
        """
        if not self._login:
            logger.warning("请先登录")
            UNAUTHORIZED_RESPONSE = {
                "errInfo": "未登录",
                "payload": {}
            }
            return Response(json.dumps(UNAUTHORIZED_RESPONSE))

        attempt = 0
        while attempt < max_attempts:
            result_code, result = self._hq.query_data(req, service_type, buffer_size)

            if result_code == 0:
                response = Response(result)
                if response.errInfo != "":
                    logger.info(f"查询数据错误信息: {response.errInfo}")
                response.convert_data()
                logger.debug(f"查询执行: {req}, 类型: {service_type}")
                return response
            elif result_code == -1:
                current_size_mb = buffer_size / (1024 * 1024)
                new_size_mb = (buffer_size * 2) / (1024 * 1024)
                logger.info(f"缓冲区大小不足。当前大小: {current_size_mb:.2f} MB, "
                            f"新的大小: {new_size_mb:.2f} MB")
                time.sleep(0.1)
                buffer_size *= 2
                attempt += 1
                if attempt == max_attempts:
                    return error_response(f"达到最大尝试次数，错误代码: {result_code}, "
                                          f"请求: {req}, 最终缓冲区大小: {buffer_size}")
            else:
                return error_response(f"错误代码: {result_code}, 未找到请求数据: {req}")

        return error_response(f"意外错误: 达到最大尝试次数，请求: {req}")

    def subscribe(self, req: str, service_type: str, callback: c.CFUNCTYPE) -> Response:
        """订阅实时行情数据。

        Args:
            req (str): 订阅请求字符串，如订阅 ID 或其他参数。
            service_type (str): 服务类型，默认为 "push"。
            callback (CFUNCTYPE): 回调函数，用于处理订阅数据，需为 CFUNCTYPE(None, c_char_p) 类型。

        Returns:
            Response: 包含订阅结果的响应对象。
        """
        result_code, result = self._hq.subscribe(req, service_type, callback=callback)
        if result_code == 0:
            response = Response(result)
            if response.errInfo != "":
                logger.info(f"订阅错误信息: {response.errInfo}")
            return response
        else:
            return error_response(f"错误代码: {result_code}, 订阅失败: {req} {service_type}")

    def unsubscribe(self, subscribe_id: str) -> Response:
        """取消订阅实时行情数据。

        Args:
            subscribe_id (str): 订阅 ID，由 subscribe 方法返回。

        Returns:
            Response: 包含取消订阅结果的响应对象。
        """
        result_code, result = self._hq.unsubscribe(subscribe_id)
        if result_code == 0:
            response = Response(result)
            if response.errInfo != "":
                logger.info(f"订阅错误信息: {response.errInfo}")
            return response
        else:
            return error_response(f"错误代码: {result_code}, 退订失败: {subscribe_id}")

    def help(self, req: str = "") -> str:
        """获取帮助信息。

        Args:
            req (str, optional): 查询条件，如 "about"。默认为空字符串。

        Returns:
            str: 帮助信息字符串。
        """
        result_code, result = self._hq.help(req)
        response = Response(result)
        return response.payload.help

    def history_minute_time_data(self, ths_code: str, date: str, fields: Optional[List[str]] = None) -> Response:
        """获取分钟级历史数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            date (str): 日期，格式为 YYYYMMDD。
            fields (List[str], optional): 指定返回的字段列表。默认为 None。

        Returns:
            Response: 包含分钟级历史数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            InvalidDateError: 如果日期格式无效。
        """
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if not re.match(r'^\d{8}$', date):
            return error_response("日期格式必须为 YYYYMMDD")

        ths_code = ths_code.upper()
        data_type = "1,10,13,19,40"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=207&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&datatype={data_type}&date={date}")
        response = self.query_data(req)

        response.payload.data = [
            {**entry, "时间": _int2time(entry["时间"])} if "时间" in entry else entry
            for entry in response.payload.data
            if "时间" not in entry or _is_valid_time(entry["时间"])
        ]

        if fields:
            response.payload.data = [entry for entry in response.payload.data if
                                     all(field in entry for field in fields)]
        return response

    def security_bars(self, ths_code: str, start: int, end: int, adjust: str, interval: int) -> Response:
        """获取 K 线数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            start (int): 开始时间，格式取决于周期（日级别为 YYYYMMDD，分钟级别为时间戳）。
            end (int): 结束时间，格式同 start。
            adjust (str): 复权类型，来自 Adjust 类（如 Adjust.FORWARD）。
            interval (int): 周期类型，来自 Interval 类（如 Interval.DAY）。

        Returns:
            Response: 包含 K 线数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            ValueError: 如果复权类型或周期类型无效。
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if adjust not in Adjust.all_types():
            return error_response(f"无效的复权类型: {adjust}")
        if interval not in Interval.all_types():
            return error_response(f"无效的周期类型: {interval}")

        data_type = "1,7,8,9,11,13,19"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=210&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}"
               f"&fuquan={adjust}&datatype={data_type}&period={interval}")
        response = self.query_data(req)

        if interval in Interval.minute_intervals():
            for entry in response.payload.data:
                if "时间" in entry:
                    entry["时间"] = _int2time(entry["时间"])
        else:
            for entry in response.payload.data:
                if "时间" in entry:
                    entry["时间"] = datetime.datetime.strptime(str(entry["时间"]), "%Y%m%d")
        return response

    def get_block_data(self, block_id: int) -> Response:
        """获取板块数据。

        Args:
            block_id (int): 板块 ID，如 0xE 表示沪深A股。
                        0x4 沪封闭式基金
                        0x5 深封闭式基金
                        0x6 沪深封闭式基金
                        0xE 沪深A股
                        0x15 沪市A股
                        0x1B 深市A股
                        0xD2 全部指数
                        0xC5E3 北京A股
                        0xCFE4 创业板
                        0xCBE5 科创板
                        0xDBC6 风险警示
                        0xDBC7 退市整理
                        0xF026 行业和概念
                        0xCE5E 概念
                        0xCE5F 行业
                        0xdffb 地域
                        0xD385 国内外重要指数
                        0xDB5E 股指期货
                        0xCE3F 上证系列指数
                        0xCE3E 深证系列指数
                        0xCE3D 中证系列指数
                        0xC2B0 北证系列指数
                        0xCFF3 ETF基金
                        0xC6A6 全部A股
                        0xEF8C LOF基金
                        0xD811 分级基金
                        0xD90C T+0基金
                        0xC7B1 沪REITs
                        0xC7A0 深REITs
                        0xC89C 沪深REITs
                        0xCE14 可转债
                        0xCE17 国债
                        0xCE0B 上证债券
                        0xCE0A 深证债券
                        0xCE12 回购
                        0xCE11 贴债
                        0xCE16 地方债
                        0xCE15 企业债
                        0xD8D4 小公募

        Returns:
            Response: 包含板块数据的响应对象。

        Raises:
            ValueError: 如果 block_id 未提供。
        """
        if not block_id:
            return error_response("必须提供板块 ID")
        req = (f"id=7&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&sortbegin=0&sortcount=0&sortorder=D&sortid=55&blockid={block_id:x}&reqflag=blockserver")
        return self.query_data(req, "bk")

    def get_block_components(self, link_code: str) -> Response:
        """获取板块成分股数据。

        Args:
            link_code (str): 板块代码，如 'URFI881273'。

        Returns:
            Response: 包含成分股数据的响应对象。

        Raises:
            ValueError: 如果 link_code 未提供。
        """
        if not link_code:
            return error_response("必须提供板块代码")
        req = (f"id=7&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&sortbegin=0&sortcount=0&sortorder=D&sortid=55&linkcode={link_code}")
        return self.query_data(req, "bk")

    def get_transaction_data(self, ths_code: str, start: int, end: int) -> Response:
        """获取3秒 tick 成交数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            start (int): 开始时间戳。
            end (int): 结束时间戳。

        Returns:
            Response: 包含成交数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            ValueError: 如果开始时间戳大于或等于结束时间戳。
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if start >= end:
            return error_response("开始时间戳必须小于结束时间戳")
        data_type = "1,5,10,12,18,49"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=205&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}"
               f"&datatype={data_type}&TraceDetail=0")
        return self.query_data(req)

    def get_super_transaction_data(self, ths_code: str, start: int, end: int) -> Response:
        """获取3秒超级盘口数据（包含委托档位）。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            start (int): 开始时间戳。
            end (int): 结束时间戳。

        Returns:
            Response: 包含超级盘口数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            ValueError: 如果开始时间戳大于或等于结束时间戳。
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if start >= end:
            return error_response("开始时间戳必须小于结束时间戳")
        data_type = ("1,5,7,10,12,13,14,18,19,20,21,25,26,27,28,29,31,32,33,34,35,49,"
                     "69,70,92,123,125,150,151,152,153,154,155,156,157,45,66,661,102,103,"
                     "104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,123,125")
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=205&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}"
               f"&datatype={data_type}&TraceDetail=0")
        return self.query_data(req)

    def get_l2_transaction_data(self, ths_code: str, start: int, end: int) -> Response:
        """获取 L2 成交数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            start (int): 开始时间戳。
            end (int): 结束时间戳。

        Returns:
            Response: 包含 L2 成交数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            ValueError: 如果开始时间戳大于或等于结束时间戳。
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if start >= end:
            return error_response("开始时间戳必须小于结束时间戳")
        data_type = "5,10,12,13"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=220&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}&datatype={data_type}")
        return self.query_data(req)

    def query_ths_industry(self) -> Response:
        """获取行业板块数据。

        Returns:
            Response: 包含行业板块数据的响应对象。
        """
        return self.get_block_data(0xCE5F)

    def query_ths_concept(self) -> Response:
        """获取概念板块数据。

        Returns:
            Response: 包含概念板块数据的响应对象。
        """
        return self.get_block_data(0xCE5E)

    def query_ths_conbond(self) -> Response:
        """获取可转债板块数据。

        Returns:
            Response: 包含可转债板块数据的响应对象。
        """
        return self.get_block_data(0xCE14)

    def query_ths_index(self) -> Response:
        """获取指数板块数据。

        Returns:
            Response: 包含指数板块数据的响应对象。
        """
        return self.get_block_data(0xD2)

    def query_ths_etf(self) -> Response:
        """获取 ETF 板块数据。

        Returns:
            Response: 包含 ETF 板块数据的响应对象。
        """
        return self.get_block_data(0xCFF3)

    def query_ths_etf_t0(self) -> Response:
        """获取 ETF T+0 板块数据。

        Returns:
            Response: 包含 ETF T+0 板块数据的响应对象。
        """
        return self.get_block_data(0xD90C)

    def download(self, ths_code: str, start: Optional[Any] = None, end: Optional[Any] = None,
                 adjust: str = Adjust.NONE, period: str = "max", interval: int = Interval.DAY,
                 count: int = -1) -> Response:
        """获取 K 线数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。
            start (Any, optional): 开始时间，格式取决于周期。默认为 None。
            end (Any, optional): 结束时间，格式同 start。默认为 None。
            adjust (str, optional): 复权类型，默认为 Adjust.NONE。
            period (str, optional): 周期范围，默认为 "max"。
            interval (int, optional): 周期类型，默认为 Interval.DAY。
            count (int, optional): 数据条数，优先于 start/end，默认为 -1。

        Returns:
            Response: 包含 K 线数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
            ValueError: 如果复权类型、周期类型无效，或 start/end 类型不一致。
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")
        if adjust not in Adjust.all_types():
            return error_response(f"无效的复权类型: {adjust}")
        if interval not in Interval.all_types():
            return error_response(f"无效的周期类型: {interval}")
        if start is not None and end is not None and type(start) is not type(end):
            return error_response("'start' 和 'end' 必须为相同类型")
        if (start is None and end is not None) or (start is not None and end is None):
            return error_response("'start' 和 'end' 必须同时提供或同时为 None")

        if interval in Interval.day_and_above_intervals():
            if start is None or end is None:
                if period == "max":
                    intervals = {
                        Interval.DAY: (-365 * 100, 0),
                        Interval.WEEK: (-52 * 100, 0),
                        Interval.MONTH: (-12 * 100, 0),
                        Interval.QUARTER: (-4 * 100, 0),
                        Interval.YEAR: (-100, 0),
                    }
                    start, end = intervals.get(interval, (-365 * 100, 0))
            else:
                if isinstance(start, str):
                    start = start.replace("-", "")
                    end = end.replace("-", "")
                elif isinstance(start, datetime.datetime):
                    start = int(start.strftime("%Y%m%d"))
                    end = int(end.strftime("%Y%m%d"))

                if end < start:
                    return error_response("结束时间必须大于开始时间")

        if interval in Interval.minute_intervals():
            if start is None or end is None:
                if period == "max":
                    start, end = -1000, 0
            else:
                if isinstance(start, str) and isinstance(end, str):
                    start = start.replace("-", "")
                    end = end.replace("-", "")
                    if len(start) == 8 and len(end) == 8:
                        dt = datetime.datetime.strptime(start, "%Y%m%d")
                        dt = dt.replace(hour=9, minute=15, tzinfo=tz)
                        start = _time2int(dt)

                        dt = datetime.datetime.strptime(end, "%Y%m%d")
                        dt = dt.replace(hour=15, minute=30, tzinfo=tz)
                        end = _time2int(dt)

                elif isinstance(start, int) and isinstance(end, int):
                    try:
                        if len(str(start)) == 8 or len(str(end)) == 8:
                            dt = datetime.datetime.strptime(str(start), "%Y%m%d")
                            dt = dt.replace(hour=9, minute=15, tzinfo=tz)
                            start = _time2int(dt)

                            dt = datetime.datetime.strptime(str(end), "%Y%m%d")
                            dt = dt.replace(hour=15, minute=30, tzinfo=tz)
                            end = _time2int(dt)
                    except ValueError:
                        return error_response("'start' 和 'end' 必须是格式为 YYYYMMDD 的有效日期")
                elif isinstance(start, datetime.datetime):
                    start = _time2int(start)
                    end = _time2int(end)

                if end < start:
                    return error_response("结束时间必须大于开始时间")

        if count > 0:
            start, end = -count, 0

        data_type = "1,7,8,9,11,13,19"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=210&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}"
               f"&fuquan={adjust}&datatype={data_type}&period={interval}")
        response = self.query_data(req)

        if interval in Interval.minute_intervals():
            for entry in response.payload.data:
                if "时间" in entry:
                    entry["时间"] = _int2time(entry["时间"])
        else:
            for entry in response.payload.data:
                if "时间" in entry:
                    entry["时间"] = datetime.datetime.strptime(str(entry["时间"]), "%Y%m%d")
        return response

    def wencai_base(self, condition: str) -> Response:
        """问财基础查询。

        Args:
            condition (str): 查询条件，如 "所属行业"。

        Returns:
            Response: 包含查询结果的响应对象。
        """
        return self.query_data(condition, "wencai_base")

    def wencai_nlp(self, condition: str, domain: Optional[str] = "") -> Response:
        """问财自然语言处理查询。

        Args:
            condition (str): 查询条件，如 "涨停;所属行业;所属概念;热度排名;流通市值"。
            domain (str, optional): 查询领域，默认为空字符串。

        Returns:
            Response: 包含查询结果的响应对象。
        """
        query_type = f"wencai_nlp:{domain}" if domain else "wencai_nlp"
        return self.query_data(condition, query_type, buffer_size=1024 * 1024 * 8)

    def order_book_ask(self, ths_code: str) -> Response:
        """获取市场深度卖方数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。

        Returns:
            Response: 包含卖方数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
        """
        return self.query_data(ths_code, "order_book_ask", buffer_size=1024 * 1024 * 8)

    def order_book_bid(self, ths_code: str) -> Response:
        """获取市场深度买方数据。

        Args:
            ths_code (str): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头。

        Returns:
            Response: 包含买方数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效。
        """
        return self.query_data(ths_code, "order_book_bid", buffer_size=1024 * 1024 * 8)

    def stock_market_data(self, ths_code: Any) -> Response:
        """获取股票市场数据。

        Args:
            ths_code (str or List[str]): 证券代码，格式为10位，以 'USHA' 或 'USZA' 开头，可为单个代码或代码列表。

        Returns:
            Response: 包含股票市场数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效或多个代码的市场不一致。
        """
        if isinstance(ths_code, str):
            ths_code = [ths_code]
        elif not isinstance(ths_code, list) or not all(isinstance(code, str) for code in ths_code):
            return error_response("ths_code 必须是字符串或者字符串列表")

        for code in ths_code:
            code = code.upper()
            if len(code) != 10 or not any(code.upper().startswith(market) for market in MARKETS):
                return error_response("证券代码必须为10个字符，且以 'USHA' 或 'USZA' 开头")

        markets = {code[:4] for code in ths_code}
        if len(markets) > 1:
            return error_response("一次性查询多支股票必须市场代码相同")

        market = markets.pop()
        short_codes = ",".join([code[4:] for code in ths_code])
        data_type = "5,6,8,9,10,12,13,402,19,407,24,30,48,49,69,70,3250,920371,55,199112,264648,1968584,461256,1771976,3475914,3541450,526792,3153,592888,592890"
        req = (f"id=200&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&codelist={short_codes}&market={market}"
               f"&datatype={data_type}")
        return self.query_data(req)

    def block_market_data(self, block_code: Any) -> Response:
        """获取板块市场数据。

        Args:
            block_code (str or List[str]): 板块，格式为10位，

        Returns:
            Response: 包含股票市场数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效或多个代码的市场不一致。
        """
        if isinstance(block_code, str):
            block_code = [block_code]
        elif not isinstance(block_code, list) or not all(isinstance(code, str) for code in block_code):
            return error_response("block_code 必须是字符串或者字符串列表")

        for code in block_code:
            code = code.upper()
            if len(code) != 10 or not any(code.upper().startswith(market) for market in BLOCK_MARKETS):
                return error_response("板块代码必须为10个字符")

        markets = {code[:4] for code in block_code}
        if len(markets) > 1:
            return error_response("一次性查询多支股票必须市场代码相同")

        market = markets.pop()
        short_codes = ",".join([code[4:] for code in block_code])
        data_type = "55,38,39,13,19,92,90,5,275,276,277"
        req = (f"id=200&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&codelist={short_codes}&market={market}"
               f"&datatype={data_type}")
        return self.query_data(req, "fu")

    def block_market_data_extra(self, block_code: Any) -> Response:
        """获取板块市场数据extra。

        Args:
            block_code (str or List[str]): 板块，格式为10位，

        Returns:
            Response: 包含股票市场数据的响应对象。

        Raises:
            InvalidCodeError: 如果证券代码格式无效或多个代码的市场不一致。
        """
        if isinstance(block_code, str):
            block_code = [block_code]
        elif not isinstance(block_code, list) or not all(isinstance(code, str) for code in block_code):
            return error_response("block_code 必须是字符串或者字符串列表")

        for code in block_code:
            code = code.upper()
            if len(code) != 10 or not any(code.upper().startswith(market) for market in BLOCK_MARKETS):
                return error_response("板块代码必须为10个字符")

        markets = {code[:4] for code in block_code}
        if len(markets) > 1:
            return error_response("一次性查询多支股票必须市场代码相同")

        market = markets.pop()
        short_codes = ",".join([code[4:] for code in block_code])
        data_type = "3934664,199112,68285,592890,1771976,3250,3251,3252"
        req = (f"id=202&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&codelist={short_codes}&market={market}"
               f"&datatype={data_type}")
        return self.query_data(req, "fu")

    def ipo_today(self) -> Response:
        """查询今日 IPO 数据。

        Returns:
            Response: 包含今日 IPO 数据的响应对象。
        """
        return self.query_data("", "ipo_today")

    def ipo_wait(self) -> Response:
        """查询待申购 IPO 数据。

        Returns:
            Response: 包含待申购 IPO 数据的响应对象。
        """
        return self.query_data("", "ipo_wait")
