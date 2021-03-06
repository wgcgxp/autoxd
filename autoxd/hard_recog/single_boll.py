#coding:utf8

"""输入一个boll， 判断最佳买点
1. 计算boll线斜率, 开口宽度, cur_close与boll的垂线距离, 与均线的竖直距离
"""
from autoxd import stock, ui, myredis
from autoxd.cnn_boll.judge_boll_sign import getBolls
from autoxd.pinyin import stock_pinyin3 as jx
from autoxd.myenum import MYCOLS_NAME as colname
from autoxd.cnn_boll.judge_boll_sign import g_scope_len
import pylab as pl
import pandas as pd
import random
import numpy as np
from collections import Iterator, Iterable


class recorg_boll:
    def __init__(self, data_boll):
        pass
    
def gen_random_int(a, b):
    """在ab之间产生一个随机数"""
    return random.randint(a, b)

def load_data(code):
    df = stock.getFiveHisdatDf(code, method='mysql')
    upper, middle, lower = stock.TDX_BOLL(df['c'].values)
    
    df['upper'] = upper
    df['middle'] = middle
    df['lower'] = lower
    
    highs = pd.Series(df[colname.high]).values
    lows = pd.Series(df[colname.low]).values
    closes = pd.Series(df[colname.close]).values
    adx, pdi, mdi = stock.TDX_ADX2(highs, lows, closes)
    
    df[colname.adx] = adx
    df[colname.pdi] = pdi
    df[colname.mdi] = mdi
    rsi = stock.RSI(closes)
    df[colname.rsi] = rsi
    
    return df

def load_data_at_point(df, index, length):
    return df.iloc[index: index+length]
    
def recorg(df_boll):
    df = df_boll
    if 0: df = pd.DataFrame
    #计算参数
    
    #输出原始图片
    #closes, boll_up, boll_mid, boll_low = df[['c', 'upper','middle', colname.boll_lower]].to_list()
    closes = df['c'].values
    boll_up = df[colname.boll_upper].values
    boll_mid = pd.Series(df[colname.boll_middle]).values
    boll_low = pd.Series(df[colname.boll_lower]).values
    
    ui.drawBoll(pl, closes, boll_up, boll_mid, boll_low)
    
    #输出添加了参数的图片
    
    #输出判断
    
    pass

class boll_data_Iterator(Iterator):
    def __init__(self, code):
        df = load_data(code)
        self.df = df
        self.index = g_scope_len
    def __next__(self):
        if self.index == len(self.df):
            raise StopIteration        
        index = self.index
        df = self.df[index: index+g_scope_len]
        self.index += 1
        return df
    def __len__(self):
        return len(self.df) - g_scope_len
class boll_data_Iterable(Iterable):
    def __init__(self, code):
        self.code = code
    def __iter__(self):
        return boll_data_Iterator(self.code)
    def __len__(self):
        return len(boll_data_Iterator(self.code))

def get_data(code):
    """
    return: df ['o', 'c', 'h', 'l', 'upper', 'middle', 'lower']"""
    #df = load_data(code)
    #myredis.delkey(myredis.gen_keyname(__file__, get_data))
    df = myredis.createRedisVal(myredis.gen_keyname(__file__, get_data),
                                lambda: load_data(code)).get()
    size = len(df)
    if size > g_scope_len:
        index = gen_random_int(0, size - g_scope_len)
        df = load_data_at_point(df, index, length=g_scope_len)
    return df

def get_data_rand(code):
    """随机在结果集中取一个数据
    return : df
    """
    df = load_data(code)
    size = len(df)
    assert(size > g_scope_len)
    index = gen_random_int(g_scope_len, size - g_scope_len)
    df = load_data_at_point(df, index, length=g_scope_len)
    return df

if __name__ == "__main__":
    df = load_data(jx.PAYH)
    size = len(df)
    if size > g_scope_len:
        index = gen_random_int(0, size - g_scope_len)
        df = load_data_at_point(df, index, length=g_scope_len)
        recorg(df)
    else:
        raise Exception('长度太短') #在调试中会直接停在这里