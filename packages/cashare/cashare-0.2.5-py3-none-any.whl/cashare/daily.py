from cashare.common.dname import url1
import datetime
import pandas as pd
from cashare.common.get_data import _retry_get
from cashare.common.var_date import check_date
from cashare.common.var_token import get_token
from cashare.common.ad import calculate_adjustment_factors
# pd.set_option('display.float_format', '{:.4f}'.format)
def daily_data(ca_code,end_date=str(datetime.date.today().strftime('%Y%m%d')),start_date='19000101',adj='None'):

    ls=check_date(start_date=start_date,end_date=end_date)
    if isinstance(ls, str):
        return ls
    else:
        start_date=ls[0]
        end_date=ls[1]

    li = hg(ca_code=ca_code, token=get_token(),adj=adj, start_date=start_date, end_date=end_date)
    r = _retry_get(li, timeout=100)

    if type(r)==str:
        return r
    else:
        # print(r)
        if r.empty:
            return r
        else:

            if adj  in ['None','qfq','hfq']:
                if adj=='None':
                    r["date"] = pd.to_datetime(r["date"], unit='ms')
                    return r
                else:
                    try:
                        df = calculate_adjustment_factors(r)
                        import numpy as np
                        # 示例数据

                        # 方法1：使用np.where实现
                        df['cou'] = np.where(df['div'] != 0, 2,  # A列不为0时赋值1
                                             np.where(df['split'] != 1, 3, 1))  # B列不为1时赋值2，否则留空

                        # print(df[['date', 'close', 'div', 'split', 'cou']])

                        df = calculate_adjustment_factors(df)
                        df['for_factor'] = df['backward_factor'] / df.at[0, 'backward_factor']

                        df["date"] = pd.to_datetime(r["date"], unit='ms')
                        df.drop(columns=['cou','div',], inplace=True)
                        if adj=='qfq':


                            df[['close', 'high', 'low', 'open', ]] = df[['close', 'high', 'low', 'open', ]].multiply(df['backward_factor'], axis=0)

                            df['split']=df['split'].shift(-1).fillna(1)
                            # df['split'] = df['split']*df['split'].shift(-1).fillna(1)
                            df['split'] = df['split'][::-1].cumprod()[::-1]
                            df['volume'] = df['volume'] * df['split']
                            df.drop(columns=['split'], inplace=True)

                        else:
                            # print(22)

                            df[['close', 'high', 'low', 'open', ]] = df[['close', 'high', 'low', 'open', ]].multiply(
                                df['for_factor'], axis=0)
                            df['split'] = df['split'].cumprod()
                            df['volume'] = df['volume'] / df['split']
                            df.drop(columns=['split'], inplace=True)

                        df.drop(columns=['backward_factor', 'for_factor', ], inplace=True)
                        columns_to_round = ['open', 'high', 'low', 'close','volume']
                        df[columns_to_round] = df[columns_to_round].round(3)
                        df['change'] = (df['close'] - df['close'].shift(1)).round(2)
                        df['pct_change'] = (df['change'] / df['close'].shift(1) * 100).round(2).astype(str) + '%'

                        return df
                    except Exception as e:
                        raise ValueError(f"处理过程中发生错误: {e}", )

                        # 可以选择返回原始数据或空数据帧，或重新抛出异常
                        # 返回空DataFrame
                        # return pd.DataFrame()
            else:
                raise ValueError('adj 类型必须为None、qfq、hfq')

def hg(ca_code,adj,start_date,end_date,token):
    start_date = start_date[:4] + "-" + start_date[4:6] + "-" + start_date[6:]
    end_date = end_date[:4] + "-" + end_date[4:6] + "-" + end_date[6:]
    g_url=url1+'/us/stock/history/'+ca_code+'/'+adj+'/'+start_date+'/'+end_date+'/'+token
    return g_url


if __name__ == '__main__':
    import cashare as ca
    ca.set_token('')
    df = ca.daily_data(ca_code="aapl", start_date='2000-01-01',end_date='2025-09-22',)
    print(df)


    df = ca.daily_data(ca_code="aapl", start_date='2000-01-01', end_date='2025-09-22', adj='qfq')
    print(df)


    df = ca.daily_data(ca_code="aapl", start_date='2000-01-01', end_date='2025-09-22', adj='hfq')
    print(df)





