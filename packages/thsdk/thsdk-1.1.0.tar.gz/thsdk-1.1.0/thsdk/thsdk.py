# encoding: utf-8
# -----------------------------------------#
# Filename:     thsdk.py
#
# Description:  Financial API for fetching market data (e.g., K-line, transactions, sectors).
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
    """将整数时间戳转换为datetime对象"""
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
    """Check if the time value is valid."""
    try:
        _int2time(time_value)
        return True
    except ValueError:
        return False


def _time2int(t: datetime) -> int:
    """将datetime对象转换为整数时间戳"""
    if not t.tzinfo:
        t = t.replace(tzinfo=tz)
    return (t.minute + (t.hour << 6) + (t.day << 11) +
            (t.month << 16) + (t.year << 20)) - 0x76c00000


def _convert_data_keys(data: List[Dict]) -> List[Dict]:
    """转换数据字段名称"""
    converted_data = []
    for entry in data:
        converted_entry = {}
        for key, value in entry.items():
            key_int = int(key) if key.isdigit() else key
            converted_entry[FieldNameMap.get(key_int, key)] = value
        converted_data.append(converted_entry)
    return converted_data


def _market_code2str(market_code: str) -> str:
    """将市场代码转换为字符串表示"""
    market_map = {
        "17": "USHA",  # 沪
        "22": "USHT",  # 沪退
        "33": "USZA",  # 深圳退
        "37": "USZP",  # 深圳退
        "49": "URFI",  # 指数
        "151": "USTM",  # 北交所
    }
    return market_map.get(market_code, "")


def _market_str(market_code: str) -> str:
    """获取市场字符串表示，处理异常情况"""
    try:
        return _market_code2str(market_code)
    except ValueError:
        logger.warning(f"Unknown market code: {market_code}")
        return ""


# 市场代码列表，深圳没有USZT，USOO和UZOO为个股期权
MARKETS = ['USHI', 'USHA', 'USHB', 'USHD', 'USHJ', 'USHP', 'USHT', 'USZI', 'USZA', 'USZB', 'USZD', 'USZJ',
           'USZP', 'USOO', 'UZOO']


class Adjust:
    """K线复权类型"""
    FORWARD = "Q"  # 前复权
    BACKWARD = "B"  # 后复权
    NONE = ""  # 不复权

    @classmethod
    def all_types(cls) -> List[str]:
        """返回所有复权类型"""
        return [cls.FORWARD, cls.BACKWARD, cls.NONE]


class Interval:
    """K线周期类型"""
    MIN_1 = 0x3001  # 1分钟K线
    MIN_5 = 0x3005  # 5分钟K线
    MIN_15 = 0x300f  # 15分钟K线
    MIN_30 = 0x301e  # 30分钟K线
    MIN_60 = 0x303c  # 60分钟K线
    MIN_120 = 0x3078  # 120分钟K线
    DAY = 0x4000  # 日K线
    WEEK = 0x5001  # 周K线
    MONTH = 0x6001  # 月K线
    QUARTER = 0x6003  # 季K线
    YEAR = 0x7001  # 年K线

    @classmethod
    def minute_intervals(cls) -> List[int]:
        """返回分钟级别周期"""
        return [cls.MIN_1, cls.MIN_5, cls.MIN_15, cls.MIN_30, cls.MIN_60, cls.MIN_120]

    @classmethod
    def day_and_above_intervals(cls) -> List[int]:
        """返回日及以上级别周期"""
        return [cls.DAY, cls.WEEK, cls.MONTH, cls.QUARTER, cls.YEAR]

    @classmethod
    def all_types(cls) -> List[int]:
        """返回所有周期类型"""
        return cls.minute_intervals() + cls.day_and_above_intervals()


# 订阅数据类型：1-指数快照，2-证券快照，3-委托队列，4-逐笔委托，5-逐笔成交，5-极速盘口
DATA_CLASS_LIST = [1, 2, 3, 4, 5, 6]
DATA_CLASS_NAMES = ['index', 'stock', 'queue', 'order', 'trans', 'superstock']
# 数据类型：0xf-数据类型，0x0-交易所原始数据，0x1-使用压缩，0xf0-数据类型，0x10-更新补全后的数据
DATA_OP_TYPE = [0xf, 0x0, 0x1, 0xf0, 0x10]
# 订阅操作类型：1-全新订阅，2-取消订阅，3-该市场增加订阅代码，4-该市场删除订阅代码
SUB_OP_TYPE = [1, 2, 3, 4]

# 上交所
MarketUSHI = "USHI"  # 上海指数
MarketUSHA = "USHA"  # 上海A股
MarketUSHB = "USHB"  # 上海B股
MarketUSHD = "USHD"  # 上海债券
MarketUSHJ = "USHJ"  # 上海基金
MarketUSHP = "USHP"  # 上海退市整理
MarketUSHT = "USHT"  # 上海ST风险警示板
# 注意:上证A股还包括USHT(上证风险警示板)

# 深交所
MarketUSZI = "USZI"  # 深圳指数
MarketUSZA = "USZA"  # 深圳A股
MarketUSZB = "USZB"  # 深圳B股
MarketUSZD = "USZD"  # 深圳债券
MarketUSZJ = "USZJ"  # 深圳基金
MarketUSZP = "USZP"  # 深圳退市整理

# 北交所
MarketUSTM = "USTM"  # 北交所

# =======================
# TODO: 1.部分中文名称可能不准确，随时可能更新
#  2.重复的 value 如下，随时可能更新修复：
#  值 '代码' 重复 2 次，对应的键: [5, 7000004]
#  值 '异动类型' 重复 2 次，对应的键: [61, 330321]
#  值 '最后交易日' 重复 2 次，对应的键: [282, 877]
#  值 '净利润' 重复 2 次，对应的键: [619, 1566]
#  值 '换股比率' 重复 2 次，对应的键: [888, 134160]
#  值 '市盈(动)' 重复 2 次，对应的键: [2942, 2034120]
#  值 '板块主力净量' 重复 2 次，对应的键: [68107, 68285]
#  值 '日增仓' 重复 2 次，对应的键: [133964, 4099083]
#  值 '竞价评级' 重复 2 次，对应的键: [330322, 2018090319]
#  值 '占基金规模' 重复 2 次，对应的键: [7000001, 7000007]
#  值 '持股变动' 重复 2 次，对应的键: [7000002, 7000006]
#  值 '基金规模' 重复 2 次，对应的键: [7000003, 7000016]
FieldNameMap = {
    1: "时间",  # 不同时间区间不同含义
    5: "代码",
    6: "昨收价",
    7: "开盘价",  # open
    8: "最高价",  # high
    9: "最低价",  # low
    10: "价格",  # price
    11: "收盘价",  # close
    12: "成交方向",  # 成交方向(仅当日有效) deal_type 空换/多换
    13: "成交量",  # 股票:股; 权证:份; 债券:张
    14: "外盘成交量",  # 股票:股; 权证:份; 债券:张
    15: "内盘成交量",  # 股票:股; 权证:份; 债券:张
    16: "对倒成交量",
    17: "开盘成交量",
    18: "交易笔数",
    19: "总金额",
    20: "bid",  # 本次成交时的委托买入价 买价 在美元/人民币 看到用到
    21: "ask",  # 本次成交时的委托卖出价 卖价 在美元/人民币 看到用到
    22: "委买",  # 委买 #委托买入量 #对于个股：三档买入数量之和  #对于指数：本类指数所有股票的买入数量之和
    23: "委卖",  # 委卖  #委托卖出量 #对于个股：三档卖出数量之和 #对于指数：本类指数所有股票的卖出数量之和
    24: "买1",
    25: "买1量",
    26: "买2",
    27: "买2量",
    28: "买3",
    29: "买3量",
    30: "卖1",
    31: "卖1量",
    32: "卖2",
    33: "卖2量",
    34: "卖3",
    35: "卖3量",
    36: "指数种类",  # 0-综合指数 1-A股 2-B股
    37: "本类股票总数",
    38: "涨家数",
    39: "跌家数",
    40: "领先指标",
    41: "上涨趋势",
    42: "下跌趋势",
    43: "最近一笔成交金额",
    44: "证券名称(繁体中文)",
    45: "五日成交总量",
    46: "证券名称(英文)",
    47: "证券名称(Unicode)",
    48: "涨速",
    49: "当前量(手)",
    50: "代码(港)",
    53: "委比",
    54: "均价(中金所专用)",
    55: "名称",
    56: "挂单时间",
    60: "H股昨收",
    61: "异动类型",
    64: "状态",
    65: "持仓",
    66: "昨结",
    69: "涨停价",
    70: "跌停价",
    71: "现增仓",
    72: "今结",
    73: "昨持仓",
    74: "bid_order_id",  # 暂时在L2中看到
    75: "ask_order_id",  # 暂时在L2中看到
    80: "利息",
    82: "撤单时间",
    84: "所属行业",
    85: "盈利情况",
    89: "转让状态相关参数",
    90: "板块流通市值",
    91: "市盈率",
    92: "板块总市值",
    93: "交易单位",
    95: "52周最高",
    96: "52周最低",
    100: "现价(港)",
    102: "买6",
    103: "买6量",
    104: "卖6",
    105: "卖6量",
    106: "买7",
    107: "买7量",
    108: "卖7",
    109: "卖7量",
    110: "买8",
    111: "买8量",
    112: "卖8",
    113: "卖8量",
    114: "买9",
    115: "买9量",
    116: "卖9",
    117: "卖9量",
    118: "买10",
    119: "买10量",
    120: "卖10",
    121: "卖10量",
    122: "加权平均委买价",
    123: "总委买量",
    124: "加权平均委卖价",
    125: "总委卖量",
    130: "总手(港)",
    141: "波动性中断参考价格",
    142: "波动性中断集合竞价虚拟匹配量",
    143: "合约代码",
    144: "标的证券代码",
    145: "基础证券证券名称",
    146: "标的证券类型",
    147: "欧式美式",
    148: "认购认沽",
    149: "合约单位",
    150: "买4",
    151: "买4量",
    152: "卖4",
    153: "卖4量",
    154: "买5",
    155: "买5量",
    156: "卖5",
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
    271: "五十二周最高日期",
    272: "五十二周最低日期",
    273: "年度最高日期",
    274: "年度最低日期",
    275: "领涨股",
    276: "涨停家数",
    277: "跌停家数",
    278: "盘后最新价",
    279: "港股指数人民币成交金额",
    # 仅对个股期权有效
    280: "期权行权价",
    281: "首个交易日",
    282: "最后交易日",
    283: "期权行权日",
    284: "期权到期日",
    285: "合约版本号",
    286: "行权交割日",
    288: "标的证券前收盘",
    289: "涨跌幅限制类型",
    290: "保证金计算比例参数一",
    291: "保证金计算比例参数二",
    292: "单位保证金",
    294: "整手数",
    295: "单笔限价申报下限",
    296: "单笔限价申报上限",
    297: "单笔市价申报下限",
    298: "单笔市价申报上限",
    299: "期权合约状态信息标签",
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
    619: "净利润",
    672: "申购限额(万股)",
    675: "实际涨幅",
    676: "首日振幅",
    873: "引伸波幅",
    874: "对冲值",
    875: "街货占比",
    876: "街货量",
    877: "最后交易日",
    879: "回收价",
    880: "牛熊证种类",
    881: "标的证券",
    882: "权证类型",
    887: "行使价",
    888: "换股比率",
    890: "到期日",
    899: "财务数据项",
    900: "流通股变动量",
    981: "港元->人民币汇率",
    1002: "每股收益",
    1005: "每股净资产",
    1015: "净资产收益",
    1024: "债券规模",
    1047: "转股起始日",
    1110: "星级",
    1121: "标记",
    1322: "利率%",
    1384: "融资余额",
    1385: "融券余额",
    1386: "融资买入",
    1387: "融劵卖出",
    1566: "净利润",
    1606: "发行价",
    1612: "中签率%",
    1670: "股东总数",
    1674: "流通A股",
    2026: "评级",
    2039: "纯债价值",
    2041: "期权价值",
    2570: "卖出信号",
    2579: "机构持股比例",
    2719: "人均持股数",
    2942: "市盈(动)",
    2946: "市盈(静)",
    2947: "市净率",
    3153: "市盈TTM",
    3250: "5日涨幅",
    3251: "10日涨幅",
    3252: "20日涨幅",
    3397: "净值",
    9810: "溢价率",
    32772: "时间戳",
    68107: "板块主力净量",  # 板块 又是板块净量？ 和68285 相同
    68166: "板块主力流入",
    68167: "板块主力流出",
    68213: "板块主力净流入",
    68285: "板块主力净量",
    68759: "板块开盘价",
    133702: "细分行业",
    133778: "基差",
    133964: "日增仓",
    134071: "市销TTM",
    134072: "净资产收益TTM",
    134141: "净利润增长率",
    134143: "营业收入增长率",
    134152: "市盈率(静态)",
    134160: "换股比率",
    134162: "折溢率",
    134237: "杠杆比率",
    134238: "溢价",
    199112: "涨幅(%)",
    199643: "大单净量",
    264648: "涨跌",
    330321: "异动类型",
    330322: "竞价评级",
    330325: "涨停类型",
    330329: "涨停状态",
    331070: "今日主力增仓占比%",
    331077: "2日主力增仓占比%",
    331078: "3日主力增仓占比%",
    331079: "5日主力增仓占比%",
    331080: "10日主力增仓占比%",
    331124: "2日主力增仓排名",
    331125: "3日主力增仓排名",
    331126: "5日主力增仓排名",
    331127: "10日主力增仓排名",
    331128: "今日主力增仓排名",
    395720: "委差",
    461256: "委比%",
    461346: "年初至今涨幅",
    461438: "涨速%(10分)",
    461439: "涨速%(15分)",
    462057: "散户数量",
    526792: "振幅%",
    527198: "uk_527198",
    527526: "涨速%(3分)",
    527527: "涨速%(1分)",
    592544: "贡献度",
    592920: "市净率-1",
    592741: "机构动向",
    592888: "主力净量",
    592890: "主力净流入",
    592893: "5日大单净量",
    592894: "10日大单净量",
    592946: "多空比",
    625362: "每股公积金",
    625295: "dealNum",  #
    658784: "金叉个数",
    658785: "利好",
    658786: "利空",
    920371: "开盘涨幅",
    920372: "实体涨幅",
    920428: "股票分类标记",
    1149395: "市净率-2",
    1378761: "均价",
    1509847: "户均持股数",
    1640904: "手/笔",
    1771976: "量比",
    1968584: "换手率(%)",
    1991120: "涨幅(港)",
    2034120: "市盈(动)",
    2034121: "资产负债率",
    2097453: "流通股",
    2263506: "流通比例%",
    2427336: "均笔额",
    2646480: "H股涨跌",
    2820564: "内盘",
    3082712: "涨幅(结)%",
    3475914: "流通市值",
    3541450: "总市值",
    3934664: "板块涨速%",
    4065737: "买价",
    4099083: "日增仓",
    4131273: "卖价",
    4525375: "小单流入",
    4525376: "中单流入",
    4525377: "大单流入",
    7000001: "占基金规模",
    7000002: "持股变动",
    7000003: "基金规模",
    7000004: "代码",
    7000005: "涨幅%",
    7000006: "持股变动",
    7000007: "占基金规模",
    7000008: "业绩表现",
    7000009: "近一年收益",
    7000010: "近一周收益",
    7000011: "近一月收益",
    7000012: "近三月收益",
    7000013: "今年以来收益",
    7000014: "成立以来",
    7000015: "产品类型",
    7000016: "基金规模",
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
    17108287: "小单净额占比%",
    17108288: "中单净额占比%",
    17108289: "大单净额占比%",
    18550831: "成分股数",
    20190901: "标签",
    21302591: "小单总额",
    21302592: "中单总额",
    21302593: "大单总额",
    25496895: "小单总额占比%",
    25496896: "中单总额占比%",
    25496897: "大单总额占比%",
    189546735: "计算数据项",
    2018090319: "竞价评级",
    2018090320: "竞价异动类型及说明颜色判断字段",
    2018090410: "异动说明",
    2018090411: "竞价涨幅",
}


class THSAPIError(Exception):
    """THS API异常基类"""
    pass


class NoDataError(THSAPIError):
    """服务器未返回数据时抛出"""
    pass


class InvalidCodeError(THSAPIError):
    """无效证券代码时抛出"""
    pass


class InvalidDateError(THSAPIError):
    """无效日期格式时抛出"""
    pass


# New utility function to create an error Response

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
        """
        初始化行情服务。

        Args:
            ops: 配置字典，包含连接所需的用户名和密码等信息，例如 {"username": "user", "password": "pass"}。

        Raises:
            THSAPIError: 如果动态链接库加载失败或操作系统不受支持。
        """
        self.ops = ops or {}
        self.__lib_path = self._get_lib_path()
        self._lib = None
        self._callbacks = []  # 存储回调函数，防止垃圾回收
        self._initialize_library()

    def _get_lib_path(self) -> str:
        """
        获取动态链接库路径。

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
        """
        初始化 C 动态链接库。

        Raises:
            THSAPIError: 如果加载动态链接库失败。
        """
        try:
            self._lib = c.CDLL(self.__lib_path)
            self._lib.DataAccess.argtypes = [c.c_char_p, c.c_char_p, c.c_int, c.c_void_p]
            self._lib.DataAccess.restype = c.c_int
        except OSError as e:
            raise THSAPIError(f"加载动态链接库 {self.__lib_path} 失败: {e}")

    def call_data_access(self, operation: str = "", req: str = "", service_type: str = "",
                         callback: Optional[CFUNCTYPE] = None, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        内部方法，统一调用 DataAccess 函数，处理所有操作。

        Args:
            operation: 操作类型，可选值：connect, disconnect, query_data, subscribe, unsubscribe。
            req: 请求字符串，connect 使用 self.ops，unsubscribe 使用订阅 ID，其他操作直接传递。
            service_type: 服务类型，query_data 和 subscribe 需要，其他操作为空。
            callback: 回调函数，仅 subscribe 需要，签名需为 CFUNCTYPE(None, c.c_char_p)。
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (状态码, 返回数据或错误信息)。

        Raises:
            THSAPIError: 如果调用失败或状态码表示错误。
        """
        input_json = {
            "operation": operation,
            "service_type": service_type,
            "request": req
        }

        if operation == "connect":
            input_json["request"] = json.dumps(self.ops)

        _input = json.dumps(input_json).encode('utf-8')
        output_buffer = c.create_string_buffer(buffer_size)
        current_buffer_size = buffer_size

        status = self._lib.DataAccess(_input, output_buffer, c.c_int(current_buffer_size), callback)
        try:
            result = output_buffer.value.decode('utf-8') if output_buffer.value else ""
        except UnicodeDecodeError:
            raise THSAPIError("[thsdk] 输出缓冲区解码失败，可能包含非 UTF-8 数据")

        return status, result

    def connect(self, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        连接行情服务器。

        Args:
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (状态码, 返回数据或错误信息)。
                - 成功: 状态码=0，返回 '{"payload": {}, "errInfo": ""}'。
                - 失败: 负状态码，返回错误信息，如 '[thsdk]账户登录失败...'。

        Raises:
            THSAPIError: 如果连接失败。

        Example:
            hq = HQ({"username": "user", "password": "pass"})
            status, result = hq.connect()
            print(f"连接: 状态码={status}, 结果={result}")
        """
        return self.call_data_access("connect", buffer_size=buffer_size)

    def disconnect(self, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        断开行情服务器连接。

        Args:
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (状态码, 返回数据或错误信息)。
                - 成功: 状态码=0，返回 '{"payload": {}, "errInfo": ""}'。
                - 失败: 负状态码，返回错误信息。

        Raises:
            THSAPIError: 如果断开连接失败。

        Example:
            status, result = hq.disconnect()
            print(f"断开: 状态码={status}, 结果={result}")
        """
        return self.call_data_access("disconnect", buffer_size=buffer_size)

    def query_data(self, req: str, service_type: str, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        查询行情数据。

        Args:
            req: 查询请求字符串，例如 "id=202&instance=2384376321&zipversion=2&codelist=301024&market=USZA&datatype=2018090319,920371,3153,3475914,199112,1771976,1968584"。
            service_type: 服务类型，可选值：
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
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (状态码, 返回数据或错误信息)。
                - 成功: 状态码=0，返回 JSON 数据，如 '{"payload": {"type": "zhu", "data": [...], "dic_extra": {}, "extra": ""}, "errInfo": ""}'。
                - 失败: 负状态码，返回错误信息，如 '[thsdk]请先连接后再查询数据'。

        Raises:
            THSAPIError: 如果查询失败。

        Example:
            status, result = hq.query_data("id=202&...", "zhu")
            print(f"查询: 状态码={status}, 结果={result}")
        """
        return self.call_data_access("query_data", req, service_type, buffer_size=buffer_size)

    def subscribe(self, req: str = "", service_type: str = "push", callback: CFUNCTYPE = None,
                  buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        订阅实时行情数据。

        Args:
            req: 订阅请求字符串，可选值：
                - "": 默认订阅（每秒推送字符串数据）
                - "1": 实时价格更新（每5秒推送 JSON 数据，如 {"time": "2025-06-01 15:04:05", "price": [...]}）
                - 其他: 按默认行为处理
            service_type: 服务类型，当前仅支持 "push"。
            callback: 回调函数，接收订阅数据，签名需为 CFUNCTYPE(None, c.c_char_p)。
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (订阅 ID, 返回数据或错误信息)。
                - 成功: 订阅 ID（正整数），返回 '{"payload": {}, "errInfo": ""}'。
                - 失败: 负状态码，返回错误信息，如 '[thsdk]无效的service_type...'。

        Raises:
            ValueError: 如果 callback 不是有效的 CFUNCTYPE 类型。
            THSAPIError: 如果订阅失败。

        Example:
            @c.CFUNCTYPE(None, c.c_char_p)
            def callback(data: c.c_char_p):
                print(f"订阅数据: {data.decode('utf-8')}")

            status, result = hq.subscribe(req="1", callback=callback)
            print(f"订阅: ID={status}, 结果={result}")
        """
        if not isinstance(callback, CFUNCTYPE(None, c.c_char_p)):
            raise ValueError("回调函数必须为 ctypes.CFUNCTYPE 类型，签名需为 CFUNCTYPE(None, c_char_p)")
        self._callbacks.append(callback)  # 防止垃圾回收
        return self.call_data_access("subscribe", req, service_type, callback, buffer_size=buffer_size)

    def unsubscribe(self, subscription_id: str, buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        """
        取消订阅实时行情数据。

        Args:
            subscription_id: 订阅 ID，由 subscribe 方法返回的正整数。
            buffer_size: 输出缓冲区大小（字节），默认为 1MB。

        Returns:
            tuple[int, str]: (状态码, 返回数据或错误信息)。
                - 成功: 状态码=0，返回 '{"payload": {}, "errInfo": ""}'。
                - 失败: 负状态码，返回错误信息，如 '[thsdk]unsubscribe操作的request必须为有效的订阅ID...'。

        Raises:
            THSAPIError: 如果取消订阅失败。

        Example:
            status, result = hq.unsubscribe(123)
            print(f"取消订阅: 状态码={status}, 结果={result}")
        """
        return self.call_data_access("unsubscribe", req=str(subscription_id), buffer_size=buffer_size)

    def help(self, req: str = "", buffer_size: int = 1024 * 1024) -> tuple[int, str]:
        return self.call_data_access("help", req, "", None, buffer_size=buffer_size)


class Payload:
    """响应数据类"""

    def __init__(self, data_dict: Dict[str, Any]):
        """初始化响应数据

        Args:
            data_dict: 包含响应数据的字典
        """
        self.type: str = data_dict.get('type', "")
        self.data: List[Dict] = data_dict.get('data', [])
        self.dic_extra: Dict[str, Any] = data_dict.get('dic_extra', {})
        self.extra: Any = data_dict.get('extra', None)
        self.subscribe_id: str = data_dict.get('subscribe_id', "")  # 订阅id
        self.help: str = data_dict.get('help', "")  # 帮助信息

    def __repr__(self) -> str:
        """Provide a concise and readable string representation of the object."""
        data_preview = self.data[:2] if len(self.data) > 2 else self.data  # Show only the first 2 entries if too long
        return (f"Payload(type={self.type!r}, "
                f"data={data_preview!r}... ({len(self.data)} items), "
                f"dic_extra={self.dic_extra!r}, extra={self.extra!r}),"
                f"subscribe_id={self.subscribe_id!r}, help={self.help!r}),"
                )

    def is_empty(self) -> bool:
        """检查数据是否为空"""
        return not bool(self.data)

    def get_extra_value(self, key: str, default: Any = None) -> Any:
        """从dic_extra获取值，支持默认值"""
        return self.dic_extra.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type,
            "data": self.data,
            "dic_extra": self.dic_extra,
            "extra": self.extra,
        }


class Response:
    """API响应类"""

    def __init__(self, json_str: str):
        """初始化响应对象

        Args:
            json_str: JSON格式的响应字符串
        """
        try:
            data_dict: Dict[str, Any] = json.loads(json_str)
        except json.JSONDecodeError as e:
            data_dict: Dict[str, Any] = {}
            print(f"Invalid JSON string: {e}")

        self.errInfo: str = data_dict.get("errInfo", "")
        self.payload: Payload = Payload(data_dict.get("payload", {}))

    def __repr__(self) -> str:
        return f"Response(errInfo={self.errInfo}, payload={self.payload})"

    def convert_data(self) -> None:
        """转换数据字段名称"""
        self.payload.data = _convert_data_keys(self.payload.data or [])

    def is_success(self) -> bool:
        """检查响应是否成功"""
        return self.errInfo == ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "errInfo": self.errInfo,
            "payload": self.payload.to_dict() if self.payload else None,
        }


def error_response(err_info: str) -> Response:
    """创建错误响应对象
    Args:
        err_info: 错误信息字符串
    Returns:
        Response对象，包含错误信息和空的payload
    """
    return Response(json.dumps({
        "errInfo": err_info,
        "payload": {}
    }))


class THS:
    """同花顺金融数据API客户端"""

    def __init__(self, ops: Optional[Dict[str, Any]] = None):
        """初始化API客户端

        Args:
            ops: 配置信息，包含用户名、密码等信息
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
        """上下文管理器入口，自动连接"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动断开连接"""
        self.disconnect()

    @property
    def zip_version(self) -> int:
        """获取压缩版本号"""
        return 2

    @property
    def share_instance(self) -> int:
        """获取共享实例ID"""
        self.__share_instance += 1
        return self.__share_instance

    def connect(self, max_retries: int = 5) -> Response:
        """连接到行情服务器

        Args:
            max_retries: 最大重试次数，默认为5次，必须为正整数

        Returns:
            Response对象，表示连接结果

        Raises:
            ValueError: 如果 max_retries 小于或等于 0
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
            time.sleep(2 ** attempt)  # 指数退避
        logger.error(f"❌ 尝试 {max_retries} 次后连接失败")
        return error_response(f"尝试 {max_retries} 次后连接失败")

    def disconnect(self):
        """断开与行情服务器的连接

        Returns:
            Response对象，表示断开结果
        """
        if self._login:
            self._login = False
            self._hq.disconnect()
            logger.info("✅ 已成功断开与行情服务器的连接")
        else:
            logger.info("✅ 已经断开连接")

    def query_data(self, req: str, service_type: str = "zhu", buffer_size: int = 1024 * 1024 * 2,
                   max_attempts=5) -> Response:
        """内部方法，统一处理数据查询

        Args:
            req: 查询请求字符串
            service_type: 查询类型

        Returns:
            Response对象
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
                time.sleep(0.1)  # 休眠100毫秒后重试
                buffer_size *= 2
                output_buffer = None  # 清除缓冲区以创建新的更大缓冲区
                attempt += 1
                if attempt == max_attempts:
                    return error_response(f"达到最大尝试次数，错误代码: {result_code}, "
                                          f"请求: {req}, 最终缓冲区大小: {buffer_size}")
            else:
                return error_response(f"错误代码: {result_code}, 未找到请求数据: {req}")

        return error_response(f"意外错误: 达到最大尝试次数，请求: {req}")

    def subscribe(self, req: str, service_type: str, callback: c.CFUNCTYPE) -> Response:
        """订阅实时行情数据
        Args:
            req: 订阅请求字符串，通常为订阅ID或其他参数
            service_type: 服务类型，默认为 "push"
            callback: 回调函数，用于处理订阅数据
        Returns:
            Response对象，表示订阅结果
        """
        result_code, result = self._hq.subscribe(req, service_type, callback)
        if result_code == 0:
            response = Response(result)
            if response.errInfo != "":
                logger.info(f"订阅错误信息: {response.errInfo}")
            print(f"订阅成功: {req} {service_type}, 订阅ID: {response.payload.subscribe_id}")
            return response
        else:
            return error_response(f"错误代码: {result_code}, 订阅失败: {req} {service_type}")

    def unsubscribe(self, subscribe_id: str) -> Response:
        """取消订阅实时行情数据
        Args:
            subscribe_id: 订阅ID，由subscribe方法返回的字符串
        Returns:
            Response对象，表示取消订阅结果
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
        """获取帮助信息

           Args:
               req: 查询条件，如"about"

           Returns:
               Response，包含帮助信息
           """
        result_code, result = self._hq.help(req)
        response = Response(result)
        return response.payload.help

    def history_minute_time_data(self, ths_code: str, date: str, fields: Optional[List[str]] = None) -> Response:
        """获取分钟级历史数据

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            date: 日期，格式为YYYYMMDD
            fields: 可选，指定返回的字段列表

        Returns:
            Response对象，包含分钟级数据
        """
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("必须10个字符组成代码，开头比如 'USHA'/'USZA'")
        if not re.match(r'^\d{8}$', date):
            return error_response("日期格式必须是 YYYYMMDD")

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
        """获取K线数据

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            start: 开始时间，格式取决于周期（日级别为YYYYMMDD，分钟级别为时间戳）
            end: 结束时间，格式同start
            adjust: 复权类型（Adjust.FORWARD, Adjust.BACKWARD, Adjust.NONE）
            interval: 周期类型（Interval.MIN_1, Interval.DAY等）

        Returns:
            Response对象，包含K线数据
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以'USHA'或'USZA'开头")
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
        """获取板块数据

        Args:
            block_id:   0x4 沪封闭式基金
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
            Response对象，包含板块数据
        """
        if not block_id:
            return error_response("Block ID must be provided")
        req = (f"id=7&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&sortbegin=0&sortcount=0&sortorder=D&sortid=55&blockid={block_id:x}&reqflag=blockserver")
        return self.query_data(req, "bk")

    def get_block_components(self, link_code: str) -> Response:
        """获取板块成分股数据

        Args:
            link_code: 板块代码，如'URFI881273'

        Returns:
            Response对象，包含成分股数据
        """
        if not link_code:
            return error_response("必须提供板块代码")
        req = (f"id=7&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&sortbegin=0&sortcount=0&sortorder=D&sortid=55&linkcode={link_code}")
        return self.query_data(req, "bk")

    def get_transaction_data(self, ths_code: str, start: int, end: int) -> Response:
        """获取3秒tick成交数据

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            start: 开始时间戳
            end: 结束时间戳

        Returns:
            Response对象，包含成交数据
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("必须10个字符组成代码，开头比如 'USHA'/'USZA'")
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
        """获取3秒超级盘口数据（带委托档位）

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            start: 开始时间戳
            end: 结束时间戳

        Returns:
            Response对象，包含超级盘口数据
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("必须10个字符组成代码，开头比如 'USHA'/'USZA'")
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
        """获取L2成交数据

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            start: 开始时间戳
            end: 结束时间戳

        Returns:
            Response对象，包含L2成交数据
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("必须10个字符组成代码，开头比如 'USHA'/'USZA'")
        if start >= end:
            return error_response("开始时间戳必须小于结束时间戳")
        data_type = "5,10,12,13"
        market = ths_code[:4]
        short_code = ths_code[4:]
        req = (f"id=220&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&code={short_code}&market={market}&start={start}&end={end}&datatype={data_type}")
        return self.query_data(req)

    def query_ths_industry(self) -> Response:
        """获取行业板块数据"""
        return self.get_block_data(0xCE5F)

    def query_ths_concept(self) -> Response:
        """获取概念板块数据"""
        return self.get_block_data(0xCE5E)

    def query_ths_conbond(self) -> Response:
        """获取可转债板块数据"""
        return self.get_block_data(0xCE14)

    def query_ths_index(self) -> Response:
        """获取指数板块数据"""
        return self.get_block_data(0xD2)

    def query_ths_etf(self) -> Response:
        """获取ETF板块数据"""
        return self.get_block_data(0xCFF3)

    def query_ths_etf_t0(self) -> Response:
        """获取ETF T+0板块数据"""
        return self.get_block_data(0xD90C)

    def download(self, ths_code: str, start: Optional[Any] = None, end: Optional[Any] = None,
                 adjust: str = Adjust.NONE, period: str = "max", interval: int = Interval.DAY,
                 count: int = -1) -> Response:
        """获取K线数据并返回Response

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头
            start: 开始时间，格式取决于周期
            end: 结束时间，格式取决于周期
            adjust: 复权类型
            period: 周期范围，默认为"max"
            interval: 周期类型
            count: 数据条数，优先于start/end

        Returns:
            Response，包含K线数据
        """
        ths_code = ths_code.upper()
        if len(ths_code) != 10 or not any(ths_code.upper().startswith(market) for market in MARKETS):
            return error_response("证券代码必须为10个字符，且以'USHA'或'USZA'开头")
        if adjust not in Adjust.all_types():
            return error_response(f"无效的复权类型: {adjust}")
        if interval not in Interval.all_types():
            return error_response(f"无效的周期类型: {interval}")
        if start is not None and end is not None and type(start) is not type(end):
            return error_response("'start' 和 'end' 必须为相同类型")
        if (start is None and end is not None) or (start is not None and end is None):
            return error_response("'start' 和 'end' 必须同时提供或同时为 None")
        # 日k级别设置start，end
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

        # 分钟k级别设置start，end
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

        # count有高于start，end优先权
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
        """问财base查询

        Args:
            condition: 查询条件，如"所属行业"

        Returns:
            Response，包含查询结果
        """
        return self.query_data(condition, "wencai_base")

    def wencai_nlp(self, condition: str, domain: Optional[str] = "") -> Response:
        """问财NLP查询

        Args:
            condition: 查询条件，如"涨停;所属行业;所属概念;热度排名;流通市值"
            domain: 可选，查询领域

        Returns:
            Response，包含查询结果
        """
        query_type = f"wencai_nlp:{domain}" if domain else "wencai_nlp"
        return self.query_data(condition, query_type, buffer_size=1024 * 1024 * 8)

    def order_book_ask(self, ths_code: str) -> Response:
        """市场深度卖方

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头

        Returns:
            Response，包含查询结果
        """
        return self.query_data(ths_code, "order_book_ask", buffer_size=1024 * 1024 * 8)

    def order_book_bid(self, ths_code: str) -> Response:
        """市场深度买方

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头

        Returns:
            Response，包含查询结果
        """
        return self.query_data(ths_code, "order_book_bid", buffer_size=1024 * 1024 * 8)

    def stock_market_data(self, ths_code: Any) -> Response:
        """ 获取股票市场数据

        Args:
            ths_code: 证券代码，格式为10位，以'USHA'或'USZA'开头,list注意必须同市场代码

        Returns:
            Response，包含股票市场数据
        """

        if isinstance(ths_code, str):
            ths_code = [ths_code]  # Convert single string to list
        elif not isinstance(ths_code, list) or not all(isinstance(code, str) for code in ths_code):
            return error_response("ths_code 必须是字符串或者字符串列表")

        for code in ths_code:
            code = code.upper()
            if len(code) != 10 or not any(code.upper().startswith(market) for market in MARKETS):
                return error_response("必须10个字符组成代码，开头比如 'USHA'/'USZA'")

        markets = {code[:4] for code in ths_code}
        if len(markets) > 1:
            return error_response("一次性查询多支股票必须市场代码相同")

        market = markets.pop()  # Get the single market prefix
        short_codes = ",".join([code[4:] for code in ths_code])  # Extract short codes

        data_type = "5,6,8,9,10,12,13,402,19,407,24,30,48,49,69,70,3250,920371,55,199112,264648,1968584,461256,1771976,3475914,3541450,526792,3153,592888,592890"
        req = (f"id=200&instance={self.share_instance}&zipversion={self.zip_version}"
               f"&codelist={short_codes}&market={market}"
               f"&datatype={data_type}")
        return self.query_data(req)

    def ipo_today(self) -> Response:
        """查询今日 IPO 数据。

        该方法向 API 发送请求，获取当前日期的首次公开募股（IPO）相关信息。

        Returns:
            Response: 包含今日 IPO 数据的 HTTP 响应对象。
        """
        return self.query_data("", "ipo_today")

    def ipo_wait(self) -> Response:
        """查询待申购 IPO 数据。

        该方法向 API 发送请求，获取处于待申购阶段（例如待认购）的首次公开募股（IPO）信息。

        Returns:
            Response: 包含待申购 IPO 数据的 HTTP 响应对象。
        """
        return self.query_data("", "ipo_wait")
