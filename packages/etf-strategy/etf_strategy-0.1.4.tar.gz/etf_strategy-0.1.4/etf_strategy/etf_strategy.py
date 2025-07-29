import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import statsmodels.api as sm
from tqdm import tqdm
from datetime import timedelta
from collections import Counter
import etf_strategy
import os

def assign_score(df):
    df['换手率分组'] = pd.qcut(df['换手率'], 10, labels=False, duplicates='drop') + 1
    return df

def calc_multi_momentum_and_bias(df):
    """
    计算每个基金的月度、季度动量和均线偏移
    """
    df = df.sort_values('交易日期').copy()
    for label, window in [('3m', 63), ('1m', 21)]:
        # 动量因子
        mom_col = f'{label}_动量因子'
        ma_col = f'{label}_均线'
        bias_col = f'{label}_均线偏移'
        # 动量：当前复权价/窗口前复权价-1
        df[mom_col] = df['fq收盘价'] / df['fq收盘价'].shift(window) - 1
        # 均线和均线偏移
        df[ma_col] = df['fq收盘价'].rolling(window).mean()
        df[bias_col] = df['fq收盘价'] / df[ma_col] - 1
    return df

def rolling_slope(df, window):
    """
    对每个基金代码，计算每一天向前window天的log(价格)对时间的回归斜率
    """
    df = df.sort_values('交易日期').copy()
    log_price = np.log(df['收盘价'])
    slopes = []
    for i in range(len(df)):
        if i < window - 1:
            slopes.append(np.nan)
        else:
            y = log_price.iloc[i-window+1:i+1].values
            x = np.arange(window)
            X = np.vstack([x, np.ones(window)]).T
            slope, _ = np.linalg.lstsq(X, y, rcond=None)[0]
            slopes.append(slope)
    return pd.Series(slopes, index=df.index)

def get_etf_pattern(etf_name, theme_board_list):
    for pattern, keywords in theme_board_list.items():
        for kw in keywords:
            if kw in etf_name:
                return pattern
    return "其他"

def run_strategy_with_options(
    merged_df,
    first_days,
    score_weights,
    theme_board_list,
    select_limit=(5, 5),
    initial_cash=10000,
    min_lot=100,           # 最低购买股数，100=整百，1=可分割，0=可分割
    min_cash_weight=0.0,    # 最低现金权重，0=不保留现金，0.01=至少1%现金
    FEE_RATE = 0.0003,      # 一般为万3手续费
    MIN_FEE = 5            # 最低手续费5元
):
    monthly_selection = []
    etf_filter_day_dict = {}
    cash = initial_cash

    # 计算所有etf成立时间
    first_trade = merged_df.groupby('基金代码')['交易日期'].min().reset_index()

    for i in range(1, len(first_days)):
        trade_day = first_days.iloc[i-1]['交易日期']
        settlement_day = first_days.iloc[i]['交易日期']

        ## ETF筛选与打分
        # 只保留成立时间在当前日期一年前的etf
        one_year_before = trade_day - timedelta(days=365)
        valid_codes = first_trade[first_trade['交易日期'] <= one_year_before]['基金代码']
        etf_1yr_filter = merged_df[merged_df['基金代码'].isin(valid_codes)]
        # 只保留当前日期前一个月平均换手率大于min_turnover且交易量大于min_volume的etf
        end_mth_date = trade_day - timedelta(days=1)
        start_mth_date = end_mth_date - timedelta(days=30)
        last_month = etf_1yr_filter[(etf_1yr_filter['交易日期'] >= start_mth_date) & (etf_1yr_filter['交易日期'] <= end_mth_date)]
        stats = last_month.groupby('基金代码').agg({'换手率': 'mean', '成交量': 'mean'}).reset_index()
        selected_codes = stats[(stats['换手率'] > 0.05) & (stats['成交量'] > 5000000)]['基金代码']
        etf_filter = etf_1yr_filter[etf_1yr_filter['基金代码'].isin(selected_codes)]
        etf_filter_day = etf_filter[etf_filter["交易日期"] == trade_day].copy()
        # 标准化打分
        score_factors = ["动量_z", "alpha_z", "slope_z_1m", "slope_z_3m", "偏移_z", "vol_z_3m", "vol_z_1m"]
        etf_filter_day["动量_z"] = (etf_filter_day["1m_动量因子"] - etf_filter_day["1m_动量因子"].mean()) / etf_filter_day["1m_动量因子"].std()
        etf_filter_day["偏移_z"] = (etf_filter_day["1m_均线偏移"] - etf_filter_day["1m_均线偏移"].mean()) / etf_filter_day["1m_均线偏移"].std()
        etf_filter_day["alpha_z"] = (etf_filter_day["alpha"] - etf_filter_day["alpha"].mean()) / etf_filter_day["alpha"].std()
        etf_filter_day["vol_z_1m"] = (etf_filter_day["vol_1m"] - etf_filter_day["vol_1m"].mean()) / etf_filter_day["vol_1m"].std()
        etf_filter_day["vol_z_3m"] = (etf_filter_day["vol_3m"] - etf_filter_day["vol_3m"].mean()) / etf_filter_day["vol_3m"].std()
        etf_filter_day["slope_z_1m"] = (etf_filter_day["slope_1m"] - etf_filter_day["slope_1m"].mean()) / etf_filter_day["slope_1m"].std()
        etf_filter_day["slope_z_3m"] = (etf_filter_day["slope_3m"] - etf_filter_day["slope_3m"].mean()) / etf_filter_day["slope_3m"].std()
        etf_filter_day["score"] = np.dot(etf_filter_day[score_factors].values, score_weights)

        # 只保留得分大于0的ETF
        etf_filter_day = etf_filter_day[etf_filter_day['score'] > 0]

        # pattern 分类
        etf_filter_day["pattern"] = etf_filter_day["基金名称"].apply(
            lambda x: next((k for k, v in theme_board_list.items() if any(kw in x for kw in v)), "其他")
        )

        # 存储每期的etf_filter_day
        etf_filter_day_dict[trade_day] = etf_filter_day

        # 每个pattern最多select_limit[1]只
        etf_filter_day = etf_filter_day.sort_values("score", ascending=False)
        etf_filter_day = etf_filter_day.groupby("pattern").head(select_limit[1])
        # 选出得分最高的select_limit[0]只ETF
        top_etf = etf_filter_day.nlargest(select_limit[0], "score")[["交易日期", "基金名称", "基金代码", "收盘价", "score", "pattern"]]
        # 计算权重
        top_etf['weight'] = top_etf["score"]/top_etf["score"].sum()
        top_etf.rename(columns={"收盘价": "买入价", '交易日期': '买入日期'}, inplace=True)

        # 结算日收盘价信息
        top_etf['卖出日期'] = settlement_day
        settle_info = etf_filter[(etf_filter["交易日期"] == settlement_day) & etf_filter['基金代码']
                                .isin(top_etf['基金代码'])][["基金代码", "收盘价"]].rename(columns={"收盘价": "卖出价"})
        top_etf = top_etf.merge(settle_info, on="基金代码", how="left")
        # 卖出价为NaN时用买入价替换
        top_etf['卖出价'] = top_etf['卖出价'].fillna(top_etf['买入价'])

        # ----------- 现金优先分配，剩余资金按权重分配给ETF，能买尽量买 -----------
        min_cash = cash * min_cash_weight
        invest_cash = cash - min_cash

        alloc_cash_list = (top_etf['weight'] * invest_cash).tolist()
        prices = top_etf['买入价'].tolist()
        buy_shares = []
        buy_amounts = []

        # 先按分配资金买入
        for alloc_cash, price in zip(alloc_cash_list, prices):
            if min_lot <= 1:
                shares = alloc_cash / price
                amount = alloc_cash
            else:
                shares = int(alloc_cash // (price * min_lot)) * min_lot
                amount = shares * price
            buy_shares.append(shares)
            buy_amounts.append(amount)

        # 用剩余现金补买ETF（优先score高的ETF），直到买不动为止
        remain_cash = invest_cash - sum(buy_amounts)
        if min_lot <= 1:
            if remain_cash > 1e-8:
                idx = np.argmax(top_etf['score'].values)
                buy_shares[idx] += remain_cash / prices[idx]
                buy_amounts[idx] += remain_cash
                remain_cash = 0
        else:
            etf_order = np.argsort(-top_etf['score'].values)
            while True:
                bought = False
                for idx in etf_order:
                    price = prices[idx]
                    need = price * min_lot
                    # 预留手续费，避免现金为负
                    est_fee = max((buy_amounts[idx] + need) * FEE_RATE, MIN_FEE)
                    total_used = sum(buy_amounts) + need + sum([max(amt * FEE_RATE, MIN_FEE) if amt > 0 else 0 for amt in buy_amounts]) + est_fee
                    if cash - total_used >= 0:
                        buy_shares[idx] += min_lot
                        buy_amounts[idx] += need
                        remain_cash -= need
                        bought = True
                        break
                if not bought:
                    break

        # 最终统一计算手续费（只对总买入金额算一次）
        top_etf['买入股数'] = buy_shares
        top_etf['买入金额'] = buy_amounts
        top_etf['买入手续费'] = [max(amt * FEE_RATE, MIN_FEE) if amt > 0 else 0 for amt in buy_amounts]

        used_cash = sum(buy_amounts) + sum(top_etf['买入手续费'])
        remain_cash = cash - used_cash

        # 卖出
        sell_amounts = []
        sell_fees = []
        for idx, row in top_etf.iterrows():
            amount = row['买入股数'] * row['卖出价']
            fee = max(amount * FEE_RATE, MIN_FEE) if row['买入股数'] > 0 else 0
            sell_amounts.append(amount)
            sell_fees.append(fee)
        top_etf['卖出金额'] = sell_amounts
        top_etf['卖出手续费'] = sell_fees

        total_sell = sum(sell_amounts) - sum(sell_fees)
        cash = total_sell + remain_cash  # 下一期本金

        # 计算收益率（保留每只ETF的收益率，已扣手续费）
        top_etf['收益率'] = ((top_etf['卖出金额'] - top_etf['卖出手续费']) - (top_etf['买入金额'] + top_etf['买入手续费'])) / (top_etf['买入金额'] + top_etf['买入手续费'])
        # 如果因为比例太小而没有购买，则收益率设置为0
        top_etf['收益率'] = top_etf['收益率'].fillna(0)

        # 现金作为虚拟ETF加入
        if min_cash_weight > 0.001 or remain_cash > 0.001:
            cash_row = {
                '买入日期': trade_day,
                '基金名称': '现金',
                '基金代码': 'CASH',
                '买入价': 1.0,
                'score': 0,
                'pattern': '现金',
                'weight': remain_cash / (used_cash + remain_cash) if (used_cash + remain_cash) > 0 else 0,
                '卖出日期': settlement_day,
                '卖出价': 1.0,
                '买入股数': 1,
                '买入金额': remain_cash,
                '买入手续费': 0.0,
                '卖出金额': remain_cash,
                '卖出手续费': 0.0,
                '收益率': 0.0,
                '本期现金': remain_cash,
                '本期总资产': cash
            }
            for col in top_etf.columns:
                if col not in cash_row:
                    cash_row[col] = np.nan
            top_etf = pd.concat([top_etf, pd.DataFrame([cash_row])], ignore_index=True)

        # 重新计算所有weight（含现金）
        total_value = sum(buy_amounts) + remain_cash
        top_etf['weight'] = top_etf['买入金额'] / total_value
        top_etf.loc[top_etf['基金代码'] == 'CASH', 'weight'] = remain_cash / total_value if total_value > 0 else 0

        # 记录本期结果
        top_etf['本期收益率'] = top_etf['收益率'].dot(top_etf['weight'])
        top_etf['本期现金'] = remain_cash
        top_etf['本期总资产'] = cash
        monthly_selection.append(top_etf)

    return pd.concat(monthly_selection).reset_index(drop=True)

def last_period_selection(
    first_days,
    merged_df, 
    initial_cash,
    score_weights,
    theme_board_list,
    select_limit=(5, 5),
    min_lot=100,           # 最低购买股数，100=整百，1=可分割，0=可分割
    min_cash_weight=0.0,   # 最低现金权重，0=不保留现金，0.01=至少1%现金
    FEE_RATE=0.0003,
    MIN_FEE=5
):
    # 最后一期选股
    trade_day = first_days.iloc[-1]['交易日期']

    # 计算所有etf成立时间
    first_trade = merged_df.groupby('基金代码')['交易日期'].min().reset_index()

    # 只保留成立时间在当前日期一年前的etf
    one_year_before = trade_day - timedelta(days=365)
    valid_codes = first_trade[first_trade['交易日期'] <= one_year_before]['基金代码']
    etf_1yr_filter = merged_df[merged_df['基金代码'].isin(valid_codes)]

    # 只保留当前日期前一个月平均换手率大于5%且交易量大于500万的etf
    end_mth_date = trade_day - timedelta(days=1)
    start_mth_date = end_mth_date - timedelta(days=30)
    last_month = etf_1yr_filter[(etf_1yr_filter['交易日期'] >= start_mth_date) & (etf_1yr_filter['交易日期'] <= end_mth_date)]
    stats = last_month.groupby('基金代码').agg({'换手率': 'mean', '成交量': 'mean'}).reset_index()
    selected_codes = stats[(stats['换手率'] > 0.05) & (stats['成交量'] > 5000000)]['基金代码']
    etf_filter = etf_1yr_filter[etf_1yr_filter['基金代码'].isin(selected_codes)]

    etf_filter_day = etf_filter[etf_filter["交易日期"] == trade_day].copy()
    # 标准化打分
    score_factors = ["动量_z", "alpha_z", "slope_z_1m", "slope_z_3m", "偏移_z", "vol_z_3m", "vol_z_1m"]
    etf_filter_day["动量_z"] = (etf_filter_day["1m_动量因子"] - etf_filter_day["1m_动量因子"].mean()) / etf_filter_day["1m_动量因子"].std()
    etf_filter_day["偏移_z"] = (etf_filter_day["1m_均线偏移"] - etf_filter_day["1m_均线偏移"].mean()) / etf_filter_day["1m_均线偏移"].std()
    etf_filter_day["alpha_z"] = (etf_filter_day["alpha"] - etf_filter_day["alpha"].mean()) / etf_filter_day["alpha"].std()
    etf_filter_day["vol_z_1m"] = (etf_filter_day["vol_1m"] - etf_filter_day["vol_1m"].mean()) / etf_filter_day["vol_1m"].std()
    etf_filter_day["vol_z_3m"] = (etf_filter_day["vol_3m"] - etf_filter_day["vol_3m"].mean()) / etf_filter_day["vol_3m"].std()
    etf_filter_day["slope_z_1m"] = (etf_filter_day["slope_1m"] - etf_filter_day["slope_1m"].mean()) / etf_filter_day["slope_1m"].std()
    etf_filter_day["slope_z_3m"] = (etf_filter_day["slope_3m"] - etf_filter_day["slope_3m"].mean()) / etf_filter_day["slope_3m"].std()
    etf_filter_day["score"] = np.dot(etf_filter_day[score_factors].values, score_weights)

    # 只保留得分大于0的ETF
    etf_filter_day = etf_filter_day[etf_filter_day['score'] > 0]

    # pattern 分类
    etf_filter_day["pattern"] = etf_filter_day["基金名称"].apply(
        lambda x: next((k for k, v in theme_board_list.items() if any(kw in x for kw in v)), "其他")
    )

    # 每个pattern最多select_limit[1]只
    etf_filter_day = etf_filter_day.sort_values("score", ascending=False)
    etf_filter_day = etf_filter_day.groupby("pattern").head(select_limit[1])

    # 选出得分最高的select_limit[0]只ETF
    top_etf = etf_filter_day.nlargest(select_limit[0], "score")[["交易日期", "基金名称", "基金代码", "收盘价", "score", "pattern"]]
    top_etf['weight'] = top_etf["score"] / top_etf["score"].sum()
    top_etf.rename(columns={"收盘价": "买入价", '交易日期': '买入日期'}, inplace=True)

    # ----------- 现金优先分配，剩余资金按权重分配给ETF，能买尽量买 -----------
    min_cash = initial_cash * min_cash_weight
    invest_cash = initial_cash - min_cash

    alloc_cash_list = (top_etf['weight'] * invest_cash).tolist()
    prices = top_etf['买入价'].tolist()
    buy_shares = []
    buy_amounts = []

    # 先按分配资金买入
    for alloc_cash, price in zip(alloc_cash_list, prices):
        if min_lot <= 1:
            shares = alloc_cash / price
            amount = alloc_cash
        else:
            shares = int(alloc_cash // (price * min_lot)) * min_lot
            amount = shares * price
        buy_shares.append(shares)
        buy_amounts.append(amount)

    # 用剩余现金补买ETF（优先score高的ETF），直到买不动为止
    remain_cash = invest_cash - sum(buy_amounts)
    if min_lot <= 1:
        if remain_cash > 1e-8:
            idx = np.argmax(top_etf['score'].values)
            buy_shares[idx] += remain_cash / prices[idx]
            buy_amounts[idx] += remain_cash
            remain_cash = 0
    else:
        etf_order = np.argsort(-top_etf['score'].values)
        while True:
            bought = False
            for idx in etf_order:
                price = prices[idx]
                need = price * min_lot
                # 预留手续费，避免现金为负
                est_fee = max((buy_amounts[idx] + need) * FEE_RATE, MIN_FEE)
                total_used = sum(buy_amounts) + need + sum([max(amt * FEE_RATE, MIN_FEE) if amt > 0 else 0 for amt in buy_amounts]) + est_fee
                if initial_cash - total_used >= 0:
                    buy_shares[idx] += min_lot
                    buy_amounts[idx] += need
                    remain_cash -= need
                    bought = True
                    break
            if not bought:
                break

    # 最终统一计算手续费（只对总买入金额算一次）
    top_etf['买入股数'] = buy_shares
    top_etf['买入金额'] = buy_amounts
    top_etf['买入手续费'] = [max(amt * FEE_RATE, MIN_FEE) if amt > 0 else 0 for amt in buy_amounts]

    total_cash = min_cash + remain_cash

    # 展示结果
    top_etf['分配资金'] = top_etf['weight'] * initial_cash
    top_etf['实际买入金额'] = buy_amounts
    top_etf['剩余现金'] = total_cash

    # 现金作为虚拟ETF加入
    if min_cash_weight > 0.001 or total_cash > 0.001:
        cash_row = {
            '买入日期': trade_day,
            '基金名称': '现金',
            '基金代码': 'CASH',
            '买入价': 1.0,
            'score': 0,
            'pattern': '现金',
            'weight': total_cash / (sum(buy_amounts) + total_cash) if (sum(buy_amounts) + total_cash) > 0 else 0,
            '买入股数': 1,
            '买入金额': total_cash,
            '买入手续费': 0.0,
            '分配资金': total_cash,
            '实际买入金额': total_cash,
            '剩余现金': 0.0,
            # 其余列补NaN
        }
        for col in top_etf.columns:
            if col not in cash_row:
                cash_row[col] = np.nan
        top_etf = pd.concat([top_etf, pd.DataFrame([cash_row])], ignore_index=True)

    # 重新计算所有weight（含现金），现金的weight单独赋值
    total_value = sum(buy_amounts) + total_cash
    top_etf['weight'] = top_etf['买入金额'] / total_value
    top_etf.loc[top_etf['基金代码'] == 'CASH', 'weight'] = total_cash / total_value if total_value > 0 else 0

    return top_etf

def run_strategy_test(merged_df, first_days, score_weights, theme_board_list, select_limit = (5,5)):
    monthly_selection = []
    first_trade = merged_df.groupby('基金代码')['交易日期'].min().reset_index()
    for i in range(1, len(first_days)):
        trade_day = first_days.iloc[i-1]['交易日期']
        settlement_day = first_days.iloc[i]['交易日期']

        one_year_before = trade_day - timedelta(days=365)
        valid_codes = first_trade[first_trade['交易日期'] <= one_year_before]['基金代码']
        etf_1yr_filter = merged_df[merged_df['基金代码'].isin(valid_codes)]

        end_mth_date = trade_day - timedelta(days=1)
        start_mth_date = end_mth_date - timedelta(days=30)
        last_month = etf_1yr_filter[(etf_1yr_filter['交易日期'] >= start_mth_date) & (etf_1yr_filter['交易日期'] <= end_mth_date)]
        stats = last_month.groupby('基金代码').agg({'换手率': 'mean', '成交量': 'mean'}).reset_index()
        selected_codes = stats[(stats['换手率'] > 0.05) & (stats['成交量'] > 5000000)]['基金代码']
        etf_filter = etf_1yr_filter[etf_1yr_filter['基金代码'].isin(selected_codes)]

        etf_filter_day = etf_filter[etf_filter["交易日期"] == trade_day].copy()
        score_factors = ["动量_z", "alpha_z", "slope_z_1m", "slope_z_3m", "偏移_z", "vol_z_3m", "vol_z_1m"]
        etf_filter_day["动量_z"] = (etf_filter_day["1m_动量因子"] - etf_filter_day["1m_动量因子"].mean()) / etf_filter_day["1m_动量因子"].std()
        etf_filter_day["偏移_z"] = (etf_filter_day["1m_均线偏移"] - etf_filter_day["1m_均线偏移"].mean()) / etf_filter_day["1m_均线偏移"].std()
        etf_filter_day["alpha_z"] = (etf_filter_day["alpha"] - etf_filter_day["alpha"].mean()) / etf_filter_day["alpha"].std()
        etf_filter_day["vol_z_1m"] = (etf_filter_day["vol_1m"] - etf_filter_day["vol_1m"].mean()) / etf_filter_day["vol_1m"].std()
        etf_filter_day["vol_z_3m"] = (etf_filter_day["vol_3m"] - etf_filter_day["vol_3m"].mean()) / etf_filter_day["vol_3m"].std()
        etf_filter_day["slope_z_1m"] = (etf_filter_day["slope_1m"] - etf_filter_day["slope_1m"].mean()) / etf_filter_day["slope_1m"].std()
        etf_filter_day["slope_z_3m"] = (etf_filter_day["slope_3m"] - etf_filter_day["slope_3m"].mean()) / etf_filter_day["slope_3m"].std()
        etf_filter_day["score"] = np.dot(etf_filter_day[score_factors].values, score_weights)

        etf_filter_day = etf_filter_day[etf_filter_day['score'] > 0]
        etf_filter_day["pattern"] = etf_filter_day["基金名称"].apply(lambda x: next((k for k, v in theme_board_list.items() if any(kw in x for kw in v)), "其他"))
        etf_filter_day = etf_filter_day.sort_values("score", ascending=False)
        etf_filter_day = etf_filter_day.groupby("pattern").head(select_limit[1])
        top_etf = etf_filter_day.nlargest(select_limit[0], "score")[["交易日期", "基金名称", "基金代码", "收盘价", "score", "pattern"]]
        top_etf['weight'] = top_etf["score"]/top_etf["score"].sum()
        top_etf.rename(columns={"收盘价": "买入价", '交易日期': '买入日期'}, inplace=True)
        top_etf['卖出日期'] = settlement_day
        settle_info = etf_filter[(etf_filter["交易日期"] == settlement_day) & etf_filter['基金代码']
                                .isin(top_etf['基金代码'])][["基金代码", "收盘价"]].rename(columns={"收盘价": "卖出价"})   
        top_etf = top_etf.merge(settle_info, on="基金代码", how="left")
        top_etf['收益率'] = (top_etf['卖出价'] - top_etf['买入价']) / top_etf['买入价']
        top_etf['持有收益率'] = top_etf['收益率'].dot(top_etf['weight'])
        monthly_selection.append(top_etf)

    result = pd.concat(monthly_selection).reset_index(drop=True)
    result = result.set_index(['买入日期', '基金代码'])
    result = result.sort_index()
    HPR = result.groupby('买入日期')[['持有收益率']].mean()
    HPR['本金'] = (1 + HPR['持有收益率']).cumprod()
    start_date = HPR.index[0]
    end_date = HPR.index[-1]
    years = (end_date - start_date).days / 365.25
    annualized_return = (HPR['本金'].iloc[-1] / HPR['本金'].iloc[0]) ** (1 / years) - 1
    return annualized_return