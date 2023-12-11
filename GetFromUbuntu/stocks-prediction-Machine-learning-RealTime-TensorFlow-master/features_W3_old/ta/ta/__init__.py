import sys
import os

from _KEYS_DICT import LIST_TECH_REMOVE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from features.ta.functions import *
from features.ta.crash_points import *
from features.ta.chart import *
from features.ta.pandas import *
from features.ta.pyti import *

from pprint import pprint
from tqdm import tqdm
from statsmodels.tsa.stattools import adfuller
from features.diff import Diff

def stationary_analysis(df: pd.DataFrame, min_value = -10):
    stationary_df = pd.DataFrame(df).copy(deep=True)
    stationary_df.columns = df.columns
    stationary_results = []
    checked_columns = []
    for column in tqdm(stationary_df.columns):
        if len(df[column].unique()) <= 2: continue
        stat = adfuller(stationary_df[column])
        # Add Dicky-Fuller Test & Null-hypothesis P-value to the table
        stationary_results.append([stat[0], stat[1]])
        checked_columns.append(column)
        # print(f'{column}: {stat[0]} | {stat[1]}')

    # create a DataFrame to store the results
    results = pd.DataFrame(stationary_results, columns=['Test Statistic', 'p-value'], 
                index=checked_columns)
    
    filtered_results = results[results['Test Statistic'] >= min_value]
    
    # More negative => null hypothesis rejection => More stationary
    pprint(results.to_dict())
    pprint(filtered_results[['Test Statistic']].to_dict())
    pprint(filtered_results.index.tolist())
    return stationary_results, filtered_results

def stationise(df: pd.DataFrame, debug=False):
    # These columns generated by stationary_analysis where the adfuller test p-value is <-10
    # _, result = stationary_analysis(df, min_value=-10)
    # columns = result.index.tolist()
    columns = [
        'open', 'high', 'low', 'close', 'olap_BBAND_UPPER', 'olap_BBAND_LOWER', 'olap_BBAND_dif', 'olap_HT_TRENDLINE', 'olap_MIDPOINT', 'olap_MIDPRICE',
        'olap_SAR', 'mtum_ADXR', 'mtum_APO', 'mtum_MACD_ext', 'mtum_MACD_ext_signal', 'mtum_MFI', 'mtum_MINUS_DM', 'mtum_PLUS_DM', 'mtum_PPO', 'mtum_TRIX',
        'volu_Chaikin_AD', 'volu_OBV', 'vola_ATR', 'vola_NATR', 'vola_TRANGE', 'sti_CORREL', 'sti_LINEARREG', 'sti_LINEARREG_INTERCEPT', 'sti_STDDEV', 'sti_TSF',
        'sti_VAR', 'ma_EMA_5', 'ma_KAMA_5', 'ma_SMA_5', 'ma_TRIMA_5', 'ma_WMA_5', 'ma_EMA_10', 'ma_KAMA_10', 'ma_SMA_10', 'ma_TRIMA_10',
        'ma_WMA_10', 'ma_EMA_20', 'ma_KAMA_20', 'ma_SMA_20', 'ma_TRIMA_20', 'ma_WMA_20', 'ma_EMA_50', 'ma_KAMA_50', 'ma_SMA_50', 'ma_TRIMA_50',
        'ma_WMA_50', 'ma_EMA_100', 'ma_KAMA_100', 'ma_SMA_100', 'ma_TRIMA_100', 'ma_WMA_100', 'ma_DEMA_5', 'ma_DEMA_10', 'ma_DEMA_20', 'ma_DEMA_50',
        'ma_TEMA_5', 'ma_T3_5', 'ma_TEMA_10', 'ma_T3_10', 'ma_TEMA_20', 'ma_T3_20', 'clas_s3', 'clas_s2', 'clas_s1', 'clas_pp',
        'clas_r1', 'clas_r2', 'clas_r3', 'fibo_s2', 'fibo_s1', 'fibo_r1', 'fibo_r2', 'wood_s3', 'wood_s2', 'wood_s1',
        'wood_pp', 'wood_r1', 'wood_r2', 'wood_r3', 'demark_s1', 'demark_pp', 'demark_r1', 'cama_s3', 'cama_s2', 'cama_s1',
        'cama_r1', 'cama_r2', 'cama_r3', 'ti_acc_dist', 'ti_coppock_14_11_10', 'ti_donchian_lower_20', 'ti_donchian_center_20', 'ti_donchian_upper_20', 'ti_hma_20', 'ti_kelt_20_lower',
        'ti_kelt_20_upper', 'ti_supertrend_20', 'ti_konk_avg', 'mtum_AO_5_34', 'mtum_AR_26', 'mtum_BR_26', 'mtum_PVO_12_26_9', 'mtum_PVOs_12_26_9', 'olap_ALMA_10_60_085', 'olap_JMA_7_0',
        'olap_MCGD_10', 'olap_PWMA_10', 'olap_SINWMA_14', 'olap_SSF_10_2', 'olap_VMAP', 'olap_VWMA_10', 'perf_CUMLOGRET_1', 'perf_CUMPCTRET_1', 'perf_ha', 'tend_LDECAY_5',
        'vola_HWM', 'vola_HWU', 'vola_HWL', 'vola_KCLe_20_2', 'vola_KCUe_20_2', 'vola_THERMO_20_2_05', 'vola_THERMOma_20_2_05', 'vola_UI_14', 'volu_NVI_1', 'volu_PVI_1',
        'volu_PVOL', 'volu_PVT', 'ichi_tenkan_sen', 'ichi_kijun_sen', 'ichi_senkou_a', 'ichi_senkou_b', 'tend_renko_TR',
    ]

    # Find all existing non-stationary columns
    non_stationary_columns = [x for x in columns if x in df.columns.to_list()]
    if debug: print(f'Stationising {len(non_stationary_columns)} columns...')
    
    # Compute the logarithm difference to each non-stationary feature
    differ = Diff()
    df = differ.transform(df, non_stationary_columns)
    return df

def extract_features(df: pd.DataFrame, make_stationary=True, debug=False):
    df = df.copy()
    # Part 1 : Create all technical features
    date_index = df.index
    if debug: print('Generating TA-Lib indicators...')
    df = gel_all_TALIB_funtion(df, custom_columns=None)
    if debug: print('Generating Pivot Points...')
    df = get_all_pivots_points(df, custom_columns=None)
    if debug: print('Generating PY_TI Indicators...')
    df = get_py_TI_indicator(df, cos_cols=None)
    
    if debug: print('Generating Pandas TA Indicators...')
    df = get_all_pandas_TA_tecnical(df, cos_cols=None)
    if debug: print('Generating Pandas TU Indicators...')
    df = get_all_pandas_TU_tecnical(df, cos_cols=None)
    if debug: print('Generating Crash Points...')
    df = get_ALL_CRASH_funtion(df, custom_columns=None)

    df = df.drop(columns=LIST_TECH_REMOVE, errors='ignore')  # TODO no generarlas

    df.index = date_index
    original_length = len(df)
    df = df.dropna()
    if debug: print(f'Dropped {original_length - len(df)} from {original_length} bars')

    # Part 2 : Stationarise all non-stationary data
    if make_stationary:
        df = stationise(df, debug)
        columns_with_null = df.columns[df.isna().any()].tolist()
        assert len(columns_with_null) <= 0, "WARN Data columns have values Null, Column names :" + str(columns_with_null)
        df = df.dropna()



    if debug: print(f'Finalised with {len(df)} bars')
    return df
