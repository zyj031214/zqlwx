import pandas as pd
import matplotlib.pyplot as plt
from pyreadstat import pyreadstat
from tabulate import tabulate
from scipy import stats
from scipy.stats import somersd
import plotly.express as px

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体


def 读取SPSS数据文件(文件位置及名称, 是否保留标签值: bool = True):
    数据表, metadata = pyreadstat.read_sav(
        文件位置及名称, apply_value_formats=是否保留标签值, formats_as_ordered_category=True)
    return 数据表


def p值判断(p: float, α=0.05):
    """ p值判断 """
    if p <= α:
        return '拒绝虚无假设'
    else:
        return '接受虚无假设'


def 相关系数判断(系数: int):
    """
    判断相关系数的强弱

    """
    if 系数 >= 0.8:
        return '极强相关'
    elif 系数 >= 0.6:
        return '强相关'
    elif 系数 >= 0.4:
        return '中等强度相关'
    elif 系数 >= 0.2:
        return '弱相关'
    else:
        return '极弱相关或无相关'


def goodmanKruska_tau_y(df, x: str, y: str) -> float:
    """
    计算两个定类变量的goodmanKruska_tau_y相关系数

    df：包含定类变量的数据框
    x：数据框中作为自变量的定类变量名称
    y: 数据框中作为因变量的定类变量名称

    函数返回tau_y相关系数
    """

    cft = pd.crosstab(df[y], df[x], margins=True)
    """ 取得全部个案数目 """
    n = cft.at['All', 'All']
    """ 初始化变量 """
    E_1 = E_2 = tau_y = 0

    """ 计算E_1 """
    for i in range(cft.shape[0] - 1):
        F_y = cft['All'][i]
        E_1 += ((n - F_y) * F_y) / n
    """ 计算E_2 """
    for j in range(cft.shape[1] - 1):
        for k in range(cft.shape[0] - 1):
            F_x = cft.iloc[cft.shape[0] - 1, j]
            f = cft.iloc[k, j]
            E_2 += ((F_x - f) * f) / F_x
    """ 计算tauy """
    tau_y = (E_1 - E_2) / E_1

    return tau_y


def 有序变量描述统计函数(表名, 变量名):
    result = 表名[变量名].value_counts(sort=False)
    描述统计表 = pd.DataFrame(result)
    描述统计表['比例'] = 描述统计表['count'] / 描述统计表['count'].sum()
    描述统计表['累计比例'] = 描述统计表['比例'].cumsum()
    return 描述统计表


def 绘制柱状图(表名):
    x = 表名.index
    y = 表名['count'].values
    fig, ax2 = plt.subplots()
    ax2.bar(x, y)
    plt.show()


def 两个无序类别变量的统计分析(数据表, 自变量, 因变量):
    """ 对两个无序类别变量进行描述统计和推论统计，并给出辅助结论 """
    # 计算相关系数
    tau_y = goodmanKruska_tau_y(数据表, 自变量, 因变量)
    # 制作交互分类表
    交互表 = pd.crosstab(数据表[F"{自变量}"], 数据表[F"{因变量}"])
    交互表2 = pd.crosstab(数据表[F"{自变量}"], 数据表[F"{因变量}"],
                       margins=True, normalize=True)
    # 进行卡方检验
    chi2, p, dof, ex = stats.chi2_contingency(交互表)
    # 交互表2
    print(F"tau_y系数:{tau_y: 0.4f}", 相关系数判断(tau_y))
    print(交互表2)
    print(F"卡方值：{chi2: .2f}, p值：{p: .4f},自由度:{dof}。")
    print(p值判断(p))


def 两个有序类别变量的统计分析(数据表, 自变量, 因变量):
    """ 对两个有序类别变量进行描述统计和推论统计，并给出辅助结论 """
    x = 数据表[F"{自变量}"].cat.codes
    y = 数据表[F"{因变量}"].cat.codes
    result = somersd(x, y)
    # 制作交互分类表
    交互表 = pd.crosstab(数据表[F"{自变量}"], 数据表[F"{因变量}"])
    d_y = result.statistic
    p = result.pvalue

    print(F"Somers dy系数:{d_y: 0.4f}", 相关系数判断(d_y))
    print(tabulate(交互表))
    print(F"p值：{p: .4f}")
    print(p值判断(p))


def 两个数值变量的统计分析(数据表, 自变量, 因变量):
    """ 对两个数值变量进行统计分析，并给出辅助结论 """

    x = 数据表[自变量]
    y = 数据表[因变量]
    r, p = stats.pearsonr(x, y)

    fig = px.scatter(数据表, x="22、对于新事物，我喜欢去尝试和体验", y="总分", trendline='ols')
    fig.show()

    print(FR"决定系数r平方：{r*r :0.4f}")
    print(决定系数强弱判断(r*r))
    print(F"p值：{p: .4f}")
    print(p值判断(p))


def 决定系数强弱判断(决定系数: float):
    """ 
    <0.25       <0.06	    微弱相关或不相关
    0.25≤≤0.5	0.06≤≤0.25	低度相关
    0.5≤≤0.75	0.25≤≤0.56	中度相关
    >0.75	    >0.56	     高度相关 
    """
    if 决定系数 > 0.56:
        return "高度相关"
    elif 决定系数 > 0.25:
        return "中度相关"
    elif 决定系数 > 0.26:
        return "低度相关"
    else:
        return "微弱相关或不相关"


def 相关比率强弱判断(相关比率: float):
    """ 
    小于 0.01	微弱相关或不相关
    [0.01-0.06]	低度相关
    [0.06-0.14]	中度相关
    [0.14-0.99]	高度相关
    1	        完全相关
    """
    if 相关比率 > 0.14:
        return "高度相关"
    elif 相关比率 > 0.06:
        return "中度相关"
    elif 相关比率 > 0.01:
        return "低度相关"
    else:
        return "微弱相关或不相关"


def 类别变量与数值变量统计分析(数据表, 类别变量, 数值变量):
    """ 对数值变量的不同类别进行对比，并给出辅助结论 """
    from statsmodels.formula.api import ols

    fig = px.box(数据表, x=类别变量, y=数值变量)
    fig.show()

    model = ols(F'{数值变量} ~ {类别变量}', 数据表).fit()

    print(F"相关比率：{model.rsquared}")