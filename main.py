import pandas as pd
import os
import certifi

from data.price_loader import load_prices
from indicators.indicators import compute_indicators
from signals.signal_generator import generate_signal
from sheets.sheet_manager import update_sheet
from telegram_utils import send_telegram_message  # ✅ ADDED

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

HARD_SL = 0.10
TRAIL_SL = 0.20
MAX_HOLD_DAYS = 126


def sanitize_for_sheets(df):

    df = df.copy()

    # convert datetime columns
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")

    # round floats
    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = df[col].round(4)

    # replace NaN
    df = df.fillna("")

    # convert everything to string-safe objects
    df = df.astype(object)

    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (pd.Timestamp,)) else x)

    return df


def run():

    print("Loading universe...")

    universe = pd.read_csv("storage/universe.csv")
    symbols = universe["symbol"].tolist()

    print(f"{len(symbols)} symbols loaded")

    print("Downloading price data...")
    prices = load_prices(symbols)

    print("Computing indicators...")
    prices = compute_indicators(prices)

    print("Loading signal history...")
    signals_log = pd.read_csv("storage/signals_log.csv")

    new_signals = []

    print("Generating signals...")

    for symbol in symbols:

        stock = prices[prices["symbol"] == symbol]

        if len(stock) < 200:
            continue

        if generate_signal(stock):

            # ✅ 3-MONTH RE-ENTRY LOGIC
            recent_signal = signals_log[
                (signals_log["Symbol"] == symbol) &
                (pd.to_datetime(signals_log["Date"]) >= pd.Timestamp.today() - pd.Timedelta(days=90))
            ]

            if not recent_signal.empty:
                continue

            last = stock.iloc[-1]

            bucket = universe[universe.symbol == symbol]["bucket"].values[0]

            signal_data = {

                "Date": last["Date"],
                "Symbol": symbol,
                "Bucket": bucket,
                "EntryPrice": last["Close"],
                "CurrentPrice": last["Close"],
                "HighestPrice": last["High"],
                "5D": None,
                "20D": None,
                "3M": None,
                "6M": None,
                "ExitReason": None,
                "FinalReturn": None
            }

            new_signals.append(signal_data)

            # ✅ ENTRY TELEGRAM ALERT
            message = f"""
🚀 *NEW BUY SIGNAL*

🏢 Stock: *{symbol}*
📊 Bucket: {bucket}
💰 Entry Price: `{round(last["Close"], 2)}`
📅 Date: {last["Date"]}

⚡ Strategy: EMA Signal Engine
"""
            send_telegram_message(message)

    if len(new_signals) > 0:

        signals_log = pd.concat([signals_log, pd.DataFrame(new_signals)], ignore_index=True)

        print(f"{len(new_signals)} new signals added")

    else:

        print("No new signals today")

    print("Updating trade tracking...")

    prices["Date"] = pd.to_datetime(prices["Date"])

    for i, row in signals_log.iterrows():

        if pd.notna(row["ExitReason"]):
            continue

        symbol = row["Symbol"]

        stock = prices[prices["symbol"] == symbol].copy()

        if len(stock) == 0:
            continue

        entry_price = row["EntryPrice"]
        entry_date = pd.to_datetime(row["Date"])

        post_entry = stock[stock["Date"] >= entry_date]

        if len(post_entry) == 0:
            continue

        current_price = post_entry.iloc[-1]["Close"]
        highest_price = post_entry["High"].max()

        signals_log.loc[i, "CurrentPrice"] = current_price
        signals_log.loc[i, "HighestPrice"] = highest_price

        trading_days = len(post_entry)

        exit_reason = None

        if current_price <= entry_price * (1 - HARD_SL):
            exit_reason = "Hard SL"

        elif trading_days >= 20 and current_price <= highest_price * (1 - TRAIL_SL):
            exit_reason = "Trailing SL"

        elif (pd.Timestamp.today() - entry_date).days >= MAX_HOLD_DAYS:
            exit_reason = "Max Hold"

        if exit_reason:

            signals_log.loc[i, "ExitReason"] = exit_reason
            signals_log.loc[i, "FinalReturn"] = (current_price - entry_price) / entry_price

            # ✅ EXIT TELEGRAM ALERT
            message = f"""
❌ *EXIT SIGNAL*

🏢 Stock: *{symbol}*
📉 Reason: {exit_reason}
💰 Exit Price: `{round(current_price, 2)}`
📊 Return: `{round((current_price - entry_price) / entry_price * 100, 2)}%`
📅 Entry Date: {entry_date.date()}
"""
            send_telegram_message(message)

        # forward return tracking

        for _, r in post_entry.iterrows():

            d = (r["Date"] - entry_date).days

            if d >= 5 and pd.isna(signals_log.loc[i, "5D"]):
                signals_log.loc[i, "5D"] = (r["Close"] - entry_price) / entry_price

            if d >= 20 and pd.isna(signals_log.loc[i, "20D"]):
                signals_log.loc[i, "20D"] = (r["Close"] - entry_price) / entry_price

            if d >= 63 and pd.isna(signals_log.loc[i, "3M"]):
                signals_log.loc[i, "3M"] = (r["Close"] - entry_price) / entry_price

            if d >= 126 and pd.isna(signals_log.loc[i, "6M"]):
                signals_log.loc[i, "6M"] = (r["Close"] - entry_price) / entry_price

    print("Saving signal history...")

    signals_log["Date"] = pd.to_datetime(signals_log["Date"]).dt.strftime("%Y-%m-%d")

    signals_log.to_csv("storage/signals_log.csv", index=False)

    print("Updating Google Sheet...")

    sheet_df = sanitize_for_sheets(signals_log)
    sheet_df = sheet_df.fillna("")

    update_sheet(sheet_df)

    print("Finished successfully")


if __name__ == "__main__":
    run()
