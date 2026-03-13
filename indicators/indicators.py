from config import EMA_PERIOD, VOL_PERIOD
import pandas as pd

def compute_indicators(df):

    # Sort data
    df = df.sort_values(["symbol","Date"])

    # Force numeric types
    df["Close"] = pd.to_numeric(df["Close"])
    df["Volume"] = pd.to_numeric(df["Volume"])

    # EMA
    df["EMA100"] = df.groupby("symbol")["Close"].transform(
        lambda x: x.ewm(span=EMA_PERIOD, adjust=False).mean()
    )

    # Volume average
    df["VOL20"] = df.groupby("symbol")["Volume"].transform(
        lambda x: x.rolling(VOL_PERIOD).mean()
    )

    # Daily return
    df["DailyReturn"] = df.groupby("symbol")["Close"].pct_change()

    return df