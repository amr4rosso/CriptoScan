import pandas as pd
import pandas_ta as ta


def calculate_signals(df, mode='One per Trend', ema_short=50, ema_long=200, rsi_len=14, rsi_long=55, rsi_short=45):


    # Твой код без изменений
    df['ema_short'] = ta.ema(df['close'], length=ema_short)
    df['ema_long'] = ta.ema(df['close'], length=ema_long)
    df['rsi'] = ta.rsi(df['close'], length=rsi_len)
    df['trend_up'] = df['ema_short'] > df['ema_long']
    df['trend_down'] = df['ema_short'] < df['ema_long']
    df['long_base'] = df['trend_up'] & (df['close'] > df['ema_short'])
    df['short_base'] = df['trend_down'] & (df['close'] < df['ema_short'])
    if mode == 'Frequent':
        df['long_signal'] = df['long_base']
        df['short_signal'] = df['short_base']
    elif mode == 'Filtered':
        df['long_signal'] = df['long_base'] & (df['rsi'] > rsi_long)
        df['short_signal'] = df['short_base'] & (df['rsi'] < rsi_short)
    else:  # 'One per Trend'
        df['long_signal'] = pd.Series([False] * len(df), index=df.index)
        df['short_signal'] = pd.Series([False] * len(df), index=df.index)
        trend_was_up = False
        trend_was_down = False
        long_given = False
        short_given = False
        for i in range(len(df)):
            row = df.iloc[i]
            if row['trend_up']:
                if not trend_was_up:
                    long_given = False
                if row['long_base'] and row['rsi'] > rsi_long and not long_given:
                    df.loc[df.index[i], 'long_signal'] = True
                    long_given = True
                trend_was_up = True
                trend_was_down = False
            else:
                if not trend_was_down:
                    short_given = False
                if row['short_base'] and row['rsi'] < rsi_short and not short_given:
                    df.loc[df.index[i], 'short_signal'] = True
                    short_given = True
                trend_was_down = True
                trend_was_up = False
    return df
