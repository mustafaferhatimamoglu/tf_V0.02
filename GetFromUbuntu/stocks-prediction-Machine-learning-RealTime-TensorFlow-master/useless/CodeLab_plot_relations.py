# -*- coding: utf-8 -*-
"""https://github.com/Leci37/LecTrade LecTrade is a tool created by github user @Leci37. instagram @luis__leci Shared on 2022/11/12 .   . No warranty, rights reserved """
"""
Trade_xgboost_balance-the-imbalanced-rf-and-xgboost-with-smote.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/104c__CRrWFkX02VD662g0cdZpl_yGnrb

# Fraud analysis:
### Random Forest, XGBoost, OneClassSVM, Multivariate GMM and SMOTE, all in one cage against an imbalanced dataset.
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import warnings

from Utils import Utils_plotter, Utils_col_sele

warnings.filterwarnings('ignore')

"""## 1. Supervised learning tests

I will now test a series of different machine learning Models (no Neural Networks!) to see which one performs better, with some optimization here and there.

### 1.1 Data import, quick view and functions
"""

df = pd.read_csv("d_price/ROLL_SCALA_stock_history_MONTH_3_sep.csv",index_col=False, sep='\t')
df = df.drop(columns=Utils_col_sele.DROPS_COLUMNS)

df_score_AVG = pd.read_csv("plots_relations/A_relations_score_AVG.csv",index_col=False, sep='\t')
df_score_AVG.sort_values( by= 'DateValue', ascending=True)
df_score_AVG.describe()




def __autopct_fun(abs_values):
    #Source: https://www.holadevs.com/pregunta/64169/adding-absolute-values-to-the-labels-of-each-portion-of-matplotlibpyplotpie
    gen = iter(abs_values)
    return lambda pct: f"{pct:.1f}% ({next(gen)})"
def plot_pie_countvalues(df, colum_count , stockid= "", opion = "", path = "pie_plot_"):
    df =  df.groupby(colum_count).count()
    y = np.array(df['Date'])

    plt.figure()
    plt.pie( y , labels=df.index, autopct=__autopct_fun(y),startangle=9, shadow=True)

    name = stockid + "_"+colum_count+"_"+opion
    plt.title("Count times values:\n"+ name)
    plt.savefig(path + name + ".png")
    print(path + name + ".png")

"""Check for NaNs"""

cleaned_df = df.copy()

# You don't want the `Time` column.
cleaned_df['Date'] = pd.to_datetime(cleaned_df['Date']).map(pd.Timestamp.timestamp)
#cleaned_df = cleaned_df[columns_valids]
cleaned_df = pd.get_dummies(cleaned_df, columns = [ 'ticker'])

cleaned_df['buy_sell_point'].replace([101, -101], [100, -100], inplace=True)
#cleaned_df['buy_sell_point'].replace([-100], [0], inplace=True)#Solo para puntos de compra
#cleaned_df['buy_sell_point'].replace([100], [0], inplace=True)#Solo para puntos de venta
df = cleaned_df.dropna()

"""WOW! Seriously, no NaNs? 

Ok, let's check for the classes distributions
"""

Y_TARGET = 'buy_sell_point'
Y_target_classes = df[Y_TARGET].unique().tolist()
Y_target_classes.sort(reverse=False)
print(f"Label classes: {Y_target_classes}")
#df[Y_TARGET] = df[Y_TARGET].map(Y_target_classes )

# neg, pos = np.bincount(df[Y_TARGET])
# total = neg + pos
# print('Examples:\n    Total: {}\n    Positive: {} ({:.2f}% of total)\n'.format(
#     total, pos, 100 * pos / total))

plot_pie_countvalues(df,Y_TARGET , path ="plots_relations/roll_plot_pie_")

print('Fraud \n',df.Date[df[Y_TARGET]==1].describe(),'\n',
      '\n Non-Fraud \n',df.Date[df[Y_TARGET]==0].describe())

"""Imbalanced dataset. Might be worth to work on upsampling/downsampling of the data, but I will try without it for the moment and hope I get good results. Now let's check which variable is more correlated with the fraudulent activities. """

df.isnull().sum()
dcf = df.corrwith(df[Y_TARGET])

dcf.sort_values( ascending=False)


# import numpy as np
# # Create correlation matrix
# corr_matrix = df.corr().abs()
# # Select upper triangle of correlation matrix
# upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
# # Find features with correlation greater than 0.95
# to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]
# # Drop features
# df.drop(to_drop, axis=1, inplace=True)





dict_corr = Utils_plotter.plot_relationdist_main_val_and_all_rest_val(df, Y_TARGET, path=None)#path = "plots_relations/roll_")
df = pd.DataFrame(dict_corr.items(), columns=['Date', 'DateValue'])
df.to_csv("plots_relations/A_relations_score_AVG.csv", sep="\t", index=None)

# ymin*0.99 should be changed according to the dataset
# for ii in range(len(male)):
#     plt.text(year[ii]-0.1, ymin*0.99, male[ii]-female[ii], size=16)