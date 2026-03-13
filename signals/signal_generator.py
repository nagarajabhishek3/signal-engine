from config import MIN_DAILY_MOVE


def generate_signal(stock_df):

    # Need enough history
    if len(stock_df) < 25:
        return False

    last = stock_df.iloc[-1]

    # Condition 1: price above EMA100
    cond1 = last["Close"] > last["EMA100"]

    # Condition 2: today's volume greater than avg 20 day volume
    cond2 = last["Volume"] > last["VOL20"]

    # Condition 3: stock up >= 5%
    cond3 = last["DailyReturn"] >= MIN_DAILY_MOVE

    if cond1 and cond2 and cond3:
        return True

    return False