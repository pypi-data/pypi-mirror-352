import pandas as pd


class InstitutionTradingProcessor:
    @classmethod
    def _process_latest_trading(cls, latest_trading):
        for key in latest_trading.keys():
            if (key.find("外陸資") >= 0 or key.find("外資") >= 0):
                cls._target_institution(
                    latest_trading, latest_table['foreign'], key, volume
                )
            elif (key.find("自營商") >= 0):
                cls._target_institution(
                    latest_trading, latest_table['prop'], key, volume
                )
            elif (key.find("投信") >= 0):
                cls._target_institution(
                    latest_trading, latest_table['mutual'], key, volume
                )
            elif (key.find("三大法人") >= 0):
                cls._target_institution(
                    latest_trading, latest_table['institutional_investor'], key,
                    volume
                )
        # 計算合計
        for unit in ['stock', 'percentage']:
            # 買進總和
            latest_table['institutional_investor']['buy'][unit] = (
                latest_table['foreign']['buy'][unit] +
                latest_table['prop']['buy'][unit] +
                latest_table['mutual']['buy'][unit]
            )
            # 賣出總和
            latest_table['institutional_investor']['sell'][unit] = (
                latest_table['foreign']['sell'][unit] +
                latest_table['prop']['sell'][unit] +
                latest_table['mutual']['sell'][unit]
            )

        frames = []
        for category, trades in latest_table.items():
            temp_df = pd.DataFrame(trades).T
            temp_df['category'] = category
            frames.append(temp_df)

        latest_df = pd.concat(frames)
        latest_df = latest_df.reset_index().rename(columns={'index': 'type'})
        latest_df = latest_df[[
            'type', 'category', 'stock', 'price', 'average_price', 'percentage'
        ]]

        latest_df = pd.melt(
            latest_df,
            id_vars=['type', 'category'],
            var_name='variable',
            value_name='value'
        )

        latest_df = latest_df.pivot_table(
            index=['category', 'variable'],
            columns='type',
            values='value',
            aggfunc='first'
        )

        # 重設列名，去除多層索引
        latest_df.columns.name = None    # 去除列名稱
        latest_df = latest_df.reset_index()

        return latest_df
    @classmethod
    def _process_annual_trading(cls, trading_datas):
        return pd.DataFrame(trading_datas)

    @classmethod
    def _target_institution(cls, old_table, new_table, key, volume):
        if (key.find("買進") >= 0):
            cls._cal_institution(old_table, new_table['buy'], key, volume)
        elif (key.find("賣出") >= 0):
            cls._cal_institution(old_table, new_table['sell'], key, volume)
        elif (key.find("買賣超") >= 0):
            cls._cal_institution(
                old_table, new_table['over_buy_sell'], key, volume
            )

    @classmethod
    def _cal_institution(cls, old_table, new_table, key, volume):
        new_table['stock'] = np.round(old_table[key] / 1000, 2).item()
        new_table['percentage'] = np.round((old_table[key] / volume) * 100,
                                           2).item()
