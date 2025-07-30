import time
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from .client import FinClient
from .findata_client import FinDataClient
from .data.login_data import LoginData
from .data.market.ohlc_data import OHLCData
from .data.chart.chart_init_param_data import ChartInitParamData
from .data.chart.marker_graph_param_data import MarkerGraphParamData
from .data.chart.text_graph_param_data import TextGraphParamData
from .data.chart.financial_graph_param_data import FinancialGraphParamData
from .data.chart.line_graph_param_data import LineGraphParamData
from .data.chart.ohlc_value_data import OHLCValueData
from .data.chart.graph_value_data import GraphValueData
from .data.chart.bar_graph_param_data import BarGraphParamData
from .data.trade.order_data import OrderData
from .data.market.market_param_data import MarketParamData
from .data.market.query_param_data import QueryParamData
from .data.market.sub_ohlc_param_data import SubOHLCParamData
from .data.market.history_ohlc_param_data import HistoryOHLCParamData
from .data.market.fin_persist_read_param_data import FinPersistReadParamData
from .data.market.fin_persist_delete_param_data import FinPersistDeleteParamData
from .data.trade.trade_param_data import TradeParamData
from .data.trade.read_history_order_param_data import ReadHistoryOrderParamData
from .data.trade.read_history_tradeorder_param_data import ReadHistoryTradeOrderParamData
from .data.trade.get_account_param_data import GetAccountParamData
from .data.trade.get_orders_param_data import GetOrdersParamData
from .data.trade.get_tradeorders_param_data import GetTradeOrdersParamData
from .data.trade.get_positions_param_data import GetPositionsParamData
from .data.trade.read_exc_product_param_data import ReadExcProductParamData
from .data.trade.read_instrument_param_data import ReadInstrumentParamData
from .data.trade.save_instrument_param_data import SaveInstrumentParamData


def conncet(host: str = None, port: int = None, timeout: int = 30000) -> Tuple[bool, str]:
    return FinClient.instance().connect(host, port, timeout)


def is_connected() -> bool:
    return FinClient.instance().is_connected()


def login(user_id: str = '', password: str = '') -> Tuple[bool, str]:
    return FinClient.instance().base_handle().login(LoginData(user_id, password))


def close() -> None:
    FinClient.instance().close()


def findata_conncet(host: str = None, port: int = None, timeout: int = 60000) -> Tuple[bool, str]:
    return FinDataClient.instance().connect(host, port, timeout)


def findata_is_connected() -> bool:
    return FinDataClient.instance().is_connected()


def findata_login(user_id: str = '', password: str = '') -> Tuple[bool, str]:
    return FinDataClient.instance().base_handle().login(LoginData(user_id, password))


def findata_close() -> None:
    FinDataClient.instance().close()


def set_callback(**kwargs) -> None:
    '''
    设置行情回调
    Args:
        kwargs OnTick=None
    '''
    FinClient.instance().set_callback(**kwargs)


def set_auth_params(userid, password, host: str = None, port: int = None, timeout: int = 30000) -> Tuple[bool, str]:
    '''
    设置登录信息
    Args:
        userid:用户名
        password:密码
        host:网络地址默认为None
        port:端口号默认为None
    Returns:
        _type_: [bool,str]
    '''
    ret = conncet(host, port, timeout)
    if ret is None or ret[0] is False:
        return ret
    return login(userid, password)


def set_findata_auth_params(userid, password, host: str = None, port: int = None, timeout: int = 60000) -> Tuple[bool, str]:
    '''
    设置登录信息
    Args:
        userid:用户名
        password:密码
        host:网络地址默认为None
        port:端口号默认为None
    Returns:
        _type_: [bool,str]
    '''
    ret = findata_conncet(host, port, timeout)
    if ret is None or ret[0] is False:
        return ret
    return findata_login(userid, password)


def set_chart_init_params(params: ChartInitParamData) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().set_chart_init_params(params)


def add_line_graph(id: str, plot_index=0, value_axis_id=-1, color: str = '#FFF', style=0, price_tick=0.01, tick_valid_mul=-1.0, bind_ins_id='', bind_range='') -> Tuple[bool, str]:
    '''
    添加线图
    Args:
        id:图形ID
        plot_index:所在图层索引
        value_axis_id:所属Y轴
        color:颜色
        style:样式
        price_tick:最小变动刻度
        tick_valid_mul:显示有效的倍数 -1.0不做限制
        bind_ins_id:绑定合约
        bind_range:绑定合约周期
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_line_graph(
        LineGraphParamData(name=id, id=id, plot_index=plot_index, value_axis_id=value_axis_id,
                           style=style, color=color, price_tick=price_tick, tick_valid_mul=tick_valid_mul, bind_ins_id=bind_ins_id, bind_range=bind_range))


def add_bar_graph(id: str, plot_index=0, value_axis_id=-1, color: str = '#FFF', style=0, frame_style=2) -> Tuple[bool, str]:
    '''
    添加柱状图
    Args:
        id (str): 图形id
        plot_index (int, optional): 所在图层索引. Defaults to 0.
        value_axis_id (int, optional): 所属Y轴. Defaults to -1左边第一个Y轴.
        color (str, optional): 颜色. Defaults to '#FFF'.
        style (int, optional): 样式. Defaults to 0 box.
        frame_style (int, optional): 边框样式. Defaults to 2 线型.
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_bar_graph(
        BarGraphParamData(name=id, id=id, plot_index=plot_index, valueaxis_id=value_axis_id, style=style, frame_style=frame_style, color=color))


def add_financial_graph(id: str, plot_index=0, value_axis_id=-1, style=0, price_tick=0.01, tick_valid_mul=-1.0, bind_ins_id='', bind_range='') -> Tuple[bool, str]:
    '''
    添加线图
    Args:
        id:图形编号
        name:图形名称
        style:样式
        plot_index:所在图层索引
        value_axis_id:所属Y轴
        price_tick:最小变动刻度
        tick_valid_mul:显示有效的倍数 -1.0不做限制
        bind_ins_id:绑定合约
        bind_range:绑定合约周期
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_financial_graph(
        FinancialGraphParamData(id=id, name=id, style=style, plot_index=plot_index, value_axis_id=value_axis_id, price_tick=price_tick, tick_valid_mul=tick_valid_mul, bind_ins_id=bind_ins_id, bind_range=bind_range))


def chart_init_show() -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().chart_init_show()


def add_line_value(graphid: str, key: float = 0.0, value: float = 0.0, mill_ts: int = -1) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_graph_value(GraphValueData(graph_id=graphid, key=key, mill_ts=mill_ts, value=value))


def add_marker_graph(param: MarkerGraphParamData) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_marker_graph(param)


def add_graph_value(gv: GraphValueData) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_graph_value(gv)


def add_graph_value_list(gvl) -> Tuple[bool, str]:
    gvdl = []
    for gv in gvl:
        gvdl.append(GraphValueData(graph_id=gv[0], mill_ts=gv[1], value=gv[2]))
    return FinClient.instance().chart_handle().add_graph_value_list(gvdl)


def add_timespan_graphvalue_list(timespans: List[int], graph_values: Dict[str, List[float]] = {}, ohlc_values: Dict[str, Tuple[List[float], List[float], List[float], List[float]]] = {}) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_timespan_graphvalue_list(timespans, graph_values, ohlc_values)


def add_ohlc_value(ov: OHLCValueData) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_ohlc_value(ov)


def add_ohlc_value_list(ovl: List[OHLCValueData]) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_ohlc_value_list(ovl)


def add_ohlc(graph_id: str, o: OHLCData) -> Tuple[bool, str]:
    '''
    添加OHLC值
    Args:
        graph_id:图形名称
        o:ohlc
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_ohlc_value(OHLCValueData(graph_id=graph_id, ohlc_data=o))


def draw_text(plot_index: int, value_axis_id: int, key: float, value: float, text: str, color: str = '#FFF') -> Tuple[bool, str]:
    '''
    画文本
    Args:
        plot_index:所在图层索引
        value_axis_id:所属Y轴
        key:x轴值
        value:y轴值
        text:文本
        color:颜色
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_text_graph(
        TextGraphParamData(plot_index=plot_index, value_axis_id=value_axis_id, key=key, value=value, text=text, color=color))


def add_text_graph(param: TextGraphParamData) -> Tuple[bool, str]:
    return FinClient.instance().chart_handle().add_text_graph(param)


def draw_text_milltime(plot_index, value_axis_id, mill_ts, value, text, color='#FFF') -> Tuple[bool, str]:
    '''
    画文本
    Args:
        plot_index:所在图层索引
        value_axis_id:所属Y轴
        mill_ts:x时间戳
        value:y轴值
        text:文本
        color:颜色
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().chart_handle().add_text_graph(
        TextGraphParamData(plot_index=plot_index, value_axis_id=value_axis_id, mill_ts=mill_ts, value=value, text=text, color=color))


def set_market_params(market_names) -> Tuple[bool, str]:
    '''
    设置行情参数
    Args:
        market_names:行情名称多个时候用逗号分隔
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().market_handle().set_market_params(MarketParamData(market_names=market_names))


def subscribe(market_name: str, exchang_id: str, instrument_id: str) -> Tuple[bool, str]:
    '''
    订阅行情
    Args:
        market_name:行情名称
        exchang_id:交易所编码
        instrument_id:合约编码
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().market_handle().subscribe(QueryParamData(market_name=market_name, exchange_id=exchang_id, instrument_id=instrument_id))


def subscribe_ohlc(market_name: str, exchang_id: str, instrument_id: str, range: str) -> Tuple[bool, str]:
    '''
    订阅行情
    Args:
        market_name:行情名称
        exchang_id:交易所编码
        instrument_id:合约编码
        range:周期
    Returns:
        _type_: [bool,str]
    '''
    return FinClient.instance().market_handle().subscribe_ohlc(SubOHLCParamData(market_name=market_name, exchange_id=exchang_id, instrument_id=instrument_id, range=range))


def get_history_ohlc(market_name: str, exchang_id: str, instrument_id: str, range: str,
                     start_date: str, end_date: str, is_return_list: bool = False) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取历史ohlc数据
    Args:
        market_name:行情名称
        exchang_id:交易所编码
        instrument_id:合约编码
        range:周期
        start_date 开始日期
        end_date 结束日期
        is_return_list 是否返回list格式
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    return FinClient.instance().market_handle().get_history_ohlc(
        HistoryOHLCParamData(market_name=market_name, exchange_id=exchang_id, instrument_id=instrument_id, range=range, start_date=start_date, end_date=end_date, is_return_list=is_return_list))


def save_history_ohlc(market_name: str, ohlc_list: list) -> Tuple[bool, str]:
    '''
    保存历史ohlc数据
    Args:
        market_name:行情名称
        ohlc_list:ohlc数据
    Returns:
        _type_: [bool, str]
    '''
    return FinClient.instance().market_handle().save_history_ohlc(HistoryOHLCParamData(market_name=market_name, ohlc_list=ohlc_list))


def get_ohlc_column_types():
    return FinDataClient.instance().findata_handle().get_ohlc_column_types()


def get_tick_column_types():
    return FinDataClient.instance().findata_handle().get_tick_column_types()


def get_day_column_types():
    return FinDataClient.instance().findata_handle().get_day_column_types()


def get_instrument_column_types():
    return FinDataClient.instance().findata_handle().get_instrument_columns_types()


def get_db_column_types():
    return FinDataClient.instance().findata_handle().get_db_columns_types()


def fin_save_day_list(instrument_id: str, df, **kwargs) -> Tuple[bool, str]:
    '''
    批量按天保存day数据
    Args:
        instrument_id (str, optional) 合约编码 Defaults  to ''.
        df (DataFrame, optional): 数据集 Defaults to
        列及类型
        "ExchangeID": str, "InstrumentID": str, "TradingDay": str,
        "OpenPrice": np.float32, "HighestPrice": np.float32, "LowestPrice": np.float32, "ClosePrice": np.float32,
        "UpperLimitPrice": np.float32, "LowerLimitPrice": np.float32,
        "PreClosePrice": np.float32, "PreSettlementPrice": np.float32, "PreOpenInterest": np.int32
        compress (str, optional): 压缩方式 Defaults to 'zip'.
        level 压缩等级 Defaults to -1
        pack 序列化方式 msgpack pickle Defaults to 'msgpack'.
        vacuum 是否直接整理数据文件 Defaults to True.
        base_path 默认存取目录
    Returns:
        _type_: [bool,str]
    '''
    return FinDataClient.instance().findata_handle().fin_save_day_list(instrument_id, df, **kwargs)


def fin_read_day_list(instrument_id: str, start_date: int = 0, end_date: int = 99999999, **kwargs) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取day数据
    Args:
        instrument_id:合约编码
        start_date 开始日期
        end_date 结束日期
        base_path 默认存取目录
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    return FinDataClient.instance().findata_handle().fin_read_day_list(FinPersistReadParamData(
        instrument_id=instrument_id, start_date=start_date, end_date=end_date, base_path=base_path, period="86400", is_read_byte=True))


def fin_save_ohlc_list(instrument_id: str, df, period: str, **kwargs) -> Tuple[bool, str]:
    '''
    批量按天保存OHLC数据
    Args:
        instrument_id (str, optional) 合约编码 Defaults  to ''.
        df (DataFrame, optional): 数据集 Defaults to
        列及类型
        "ExchangeID": str, "InstrumentID": str, "TradingDay": str, "ActionDay": str, "ActionTime": str,
        "Period": np.int32, "OpenPrice": np.float32, "HighestPrice": np.float32, "LowestPrice": np.float32,
        "ClosePrice": np.float32, "CloseVolume": np.int32, "CloseBidPrice": np.float32,
        "CloseAskPrice": np.float32, "CloseBidVolume": np.int32, "CloseAskVolume": np.int32,
        "TotalTurnover": np.float64, "TotalVolume": np.int32, "OpenInterest": np.int32
        period (str, optional) 周期 Defaults  to ''
        compress (str, optional): 压缩方式 Defaults to 'zip'.
        level 压缩等级 Defaults to -1
        pack 序列化方式 msgpack pickle Defaults to 'msgpack'.
        vacuum 是否直接整理数据文件 Defaults to True.
        base_path 默认存取目录
    Returns:
        _type_: [bool,str]
    '''
    return FinDataClient.instance().findata_handle().fin_save_ohlc_list(instrument_id, df, period, **kwargs)


def fin_read_ohlc_list(instrument_id: str, start_date: int = 0, end_date: int = 99999999, period: str = '60', **kwargs) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取ohlc数据
    Args:
        instrument_id:合约编码
        start_date 开始日期
        end_date 结束日期
        period:周期
        base_path 默认存取目录
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    return FinDataClient.instance().findata_handle().fin_read_ohlc_list(FinPersistReadParamData(
        instrument_id=instrument_id, period=period, start_date=start_date, end_date=end_date, base_path=base_path, is_read_byte=True))


def fin_save_tick_list(instrument_id, df, **kwargs) -> Tuple[bool, str]:
    '''
    批量按天保存行情数据
    Args:
        instrument_id (str, optional) 合约编码 Defaults  to ''.
        df (DataFrame, optional): 数据集
        包含列
        "ExchangeID": str, "InstrumentID": str, "TradingDay": str, "ActionDay": str,
        "ActionTime": str, "ActionMSec": str, "LastPrice": np.float32,
        "LastVolume": np.int32, "BidPrice": np.float32, "BidVolume": np.int32,
        "AskPrice": np.float32, "AskVolume": np.int32, "TotalTurnover": np.float64,
        "TotalVolume": np.int32, "OpenInterest": np.int32
        compress (str, optional):zip xz 压缩方式 Defaults to 'zip'.
        level 压缩等级
        pack 序列化方式 msgpack pickle Defaults to 'msgpack'.
        vacuum 是否直接整理数据文件 Defaults to True.
        period (str, optional) 周期 Defaults  to 'tick'
        base_path 默认存取目录
    Returns:
        _type_: [bool, str]
    '''
    period = 'tick' if 'period' not in kwargs.keys() else kwargs.get('period')
    return FinDataClient.instance().findata_handle().fin_save_tick_list(instrument_id, df, period, **kwargs)


def fin_read_tick_list(instrument_id: str, start_date: int = 0, end_date: int = 99999999, **kwargs) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取basetick数据
    Args:
        instrument_id:合约编码
        start_date 起始日期
        end_date 结束日期
        base_path 默认存取目录
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    return FinDataClient.instance().findata_handle().fin_read_tick_list(
        FinPersistReadParamData(instrument_id=instrument_id, start_date=start_date,
                                end_date=end_date, base_path=base_path, is_read_byte=True))


def fin_read_db_list(instrument_id: str, start_date: int = 0, end_date: int = 99999999, period: str = '', **kwargs) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取原始数据
    Args:
        instrument_id:合约编码
        start_date 起始日期
        end_date 结束日期
        period:周期
        base_path 默认存取目录
        type_mark 数据类型 默认为MarketData
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    is_read_byte = False if 'is_read_byte' not in kwargs.keys() else bool(kwargs.get('is_read_byte'))
    type_mark = "MarketData" if 'type_mark' not in kwargs.keys() else kwargs.get('type_mark')
    return FinDataClient.instance().findata_handle().fin_read_db_list(
        FinPersistReadParamData(instrument_id=instrument_id, period=period, start_date=start_date,
                                end_date=end_date, base_path=base_path, is_read_byte=is_read_byte, type_mark=type_mark))


def fin_save_db_list(instrument_id: str, period: str, df, **kwargs) -> Tuple[bool, str]:
    '''
    保存原始数据
    Args:
        instrument_id:合约编码
        period:周期
        df:数据
        base_path 默认存取目录
        type_mark 数据类型，默认为MarketData
        vacuum 是否文件整理 默认False
    Returns:
        _type_: [bool, str]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    type_mark = "MarketData" if "type_mark" not in kwargs.keys() else kwargs.get("type_mark")
    vacuum = False if 'vacuum' not in kwargs.keys() else kwargs.get('vacuum')
    return FinDataClient.instance().findata_handle().fin_save_db_list(
        instrument_id=instrument_id, period=period, df=df, base_path=base_path,
        type_mark=type_mark, vacuum=vacuum)


def fin_read_periods(instrument_id: List[str] = []) -> Tuple[bool, str, List]:
    '''
    读取合约存储的周期
    Args:
        instrument_id:合约编码
    Returns:
        _type_: [bool, str, List]
    '''
    return FinDataClient.instance().findata_handle().fin_read_periods(instrument_id=instrument_id)


def fin_db_vacuum(instrument_id: List[str] = [], period: List[str] = []) -> Tuple[bool, str]:
    '''
    整理数据文件
    Args:
        instrument_id:合约编码
        period:周期
    Returns:
        _type_: [bool, str]
    '''
    return FinDataClient.instance().findata_handle().fin_db_vacuum(instrument_id=instrument_id, period=period)


def fin_delete_list(instrument_id: str, start_date: int, end_date: int, period: str, **kwargs) -> Tuple[bool, str]:
    '''
    获取数据
    Args:
        instrument_id:合约编码
        start_date 起始日期
        end_date 结束日期
        period:周期
        base_path 默认存取目录
    Returns:
        _type_: [bool, str]
    '''
    base_path = '' if 'base_path' not in kwargs.keys()else kwargs.get('base_path')
    return FinDataClient.instance().findata_handle().fin_delete_list(
        FinPersistDeleteParamData(instrument_id=instrument_id, period=period, start_date=start_date,
                                  end_date=end_date, base_path=base_path))


def fin_read_exc_products(exchange_id: List[str], product_id: List[str]) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取品种信息及交易时段
    Args:
        exchange_id:交易所列表
        product_id:品种列表
    Returns:
        _type_: [bool, str,df df类型为DataFrame,其中Times列为dataframe类型]
    '''
    return FinDataClient.instance().findata_handle().fin_read_exc_products(ReadExcProductParamData(exchange_id=exchange_id, product_id=product_id))


def fin_read_instruments(exchange_id: List[str] = [], instrument_id: List[str] = [], unicode: List[str] = [], like_unicode: str = '') -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取合约信息
    Args:
        exchange_id:交易所列表
        instrument_id:合约编码
        unicode:唯一编码
        like_unicode: 模糊查询unicode
    Returns:
        _type_: [bool, str, pd.DataFrame]
    '''
    return FinDataClient.instance().findata_handle().fin_read_instruments(ReadInstrumentParamData(exchange_id=exchange_id, instrument_id=instrument_id, unicode=unicode, like_unicode=like_unicode))


def fin_save_instruments(df) -> Tuple[bool, str]:
    '''
    获取品种信息及交易时段
    Args:
        df:数据dataframe
    Returns:
        _type_: [bool, str]
    '''
    return FinDataClient.instance().findata_handle().fin_save_instruments(df=df)


def fin_delete_instruments(exchange_id: List[str] = [], instrument_id: List[str] = [], unicode: List[str] = []) -> Tuple[bool, str]:
    '''
    获取合约信息
    Args:
        exchange_id:交易所列表
        instrument_id:合约编码
        unicode:唯一编码
    Returns:
        _type_: [bool, str]
    '''
    return FinDataClient.instance().findata_handle().fin_delete_instruments(ReadInstrumentParamData(exchange_id=exchange_id, instrument_id=instrument_id, unicode=unicode))


def set_trade_params(tradenames: str) -> Tuple[bool, str]:
    return FinClient.instance().trade_handle().set_trade_params(TradeParamData(trade_names=tradenames))


def insert_order(trade_name, exchange_id: str, instrument_id: str, direc: int, price: float, vol: int, open_close_type: int) -> Tuple[bool, str]:
    return FinClient.instance().trade_handle().insert_order(OrderData(exchange_id=exchange_id, instrument_id=instrument_id, price=price, direction=direc, volume=vol, investor_id=trade_name, open_close_type=open_close_type))


def cancel_order_by_data(order: OrderData) -> Tuple[bool, str]:
    return FinClient.instance().trade_handle().cancel_order(order)


def cancel_order(trade_name: str, order_id: str, instrument_id: str, order_ref: str, price: float) -> Tuple[bool, str]:
    return FinClient.instance().trade_handle().cancel_order(OrderData(investor_id=trade_name, order_id=order_id, instrument_id=instrument_id, order_ref=order_ref, price=price))


def read_history_orders(start_date: str, end_date: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().read_history_orders(ReadHistoryOrderParamData(start_date=start_date, end_date=end_date))


def read_history_tradeorders(start_date: str, end_date: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().read_history_tradeorders(ReadHistoryTradeOrderParamData(start_date=start_date, end_date=end_date))


def read_exc_products(exchange_id: List[str], product_id: List[str]) -> Tuple[bool, str, pd.DataFrame]:
    '''
    获取品种信息及交易时段
    Args:
        exchange_id:交易所列表
        product_id:品种列表
    Returns:
        _type_: [bool, str, df df类型为DataFrame,其中Times列为dataframe类型]
    '''
    return FinClient.instance().trade_handle().read_exc_products(ReadExcProductParamData(exchange_id=exchange_id, product_id=product_id))


def get_orders(trade_name: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().get_orders(GetOrdersParamData(trade_name=trade_name))


def get_tradeorders(trade_name: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().get_tradeorders(GetTradeOrdersParamData(trade_name=trade_name))


def get_positions(trade_name: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().get_positions(GetPositionsParamData(trade_name=trade_name))


def get_account(trade_name: str) -> Tuple[bool, str, list]:
    return FinClient.instance().trade_handle().get_account(GetAccountParamData(trade_name=trade_name))


def save_chart_data(file_name: str) -> Tuple[bool, str]:
    '''
    保存图数据
    Args:
        file_name 文件名称
    Returns:
        _type_: [bool, str]
    '''
    return FinClient.instance().chart_handle().save_chart_data(file_name)


def load_chart_data(file_name: str) -> Tuple[bool, str]:
    '''
    加载图数据
    Args:
        file_name 文件名称
    Returns:
        _type_: [bool, str]
    '''
    return FinClient.instance().chart_handle().load_chart_data(file_name)
