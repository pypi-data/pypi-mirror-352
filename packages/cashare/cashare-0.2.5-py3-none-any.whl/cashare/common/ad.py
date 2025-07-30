def calculate_adjustment_factors(df):
    # 按日期升序排序
    df = df.sort_values('date').reset_index(drop=True)

    # 初始化复权因子
    # df['forward_factor'] = 1.0  # 前复权因子
    df['backward_factor'] = 1.0  # 后复权因子
    import numpy as np

    # 示例数据

    # 方法1：使用np.where实现
    df['cou'] = np.where(df['div'] != 0, 2,        # A列不为0时赋值1
                np.where(df['split'] != 1, 3, 1)) # B列不为1时赋值2，否则留空

    for i in range(len(df) - 1, -1, -1):
        if i < len(df) - 1:

            if i==len(df) - 1:
                df.at[i, 'backward_factor'] =1
            else:
                cum_backward_split=df.at[i, 'backward_factor']
                current_split33 = df.at[i, 'cou']
                if current_split33  == 3:
                    next_split = df.at[i + 1, 'split']
                    # print(i)
                    # print(next_split)
                    current_split = df.at[i, 'split']
                    # print(current_split)
                    split_ratio = next_split / current_split  # 后复权：之后/当前
                    cum_backward_split *= split_ratio
                elif current_split33 == 2:
                    # print(i)
                    div_cash = df.at[i, 'div']
                    next_close = df.at[i -1, 'close']
                    # print(div_cash, next_close)
                    cum_backward_div = div_cash / next_close
                    cum_backward_split=df.at[i, 'backward_factor']*(1-cum_backward_div)
                else:
                    # print(99999)
                    df.at[i-1, 'backward_factor'] = df.at[i + 1, 'backward_factor']

                if i<0:
                    pass
                else:
                    df.at[i-1, 'backward_factor'] = cum_backward_split

    return df.iloc[:-1]
