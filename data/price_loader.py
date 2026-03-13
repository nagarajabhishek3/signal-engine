import yfinance as yf
import pandas as pd


def load_prices(symbols):

    # Yahoo allows multiple tickers in one request
    ticker_string = " ".join(symbols)

    raw = yf.download(
        tickers=ticker_string,
        period="300d",
        group_by="ticker",
        auto_adjust=True,
        threads=True,
        progress=False
    )

    data = []

    for symbol in symbols:

        try:

            # Skip if Yahoo didn't return this ticker
            if symbol not in raw.columns.levels[0]:
                continue

            stock = raw[symbol].copy()

            # Reset index to create Date column
            stock.reset_index(inplace=True)

            stock["symbol"] = symbol

            # Ensure correct column order
            stock = stock[["Date","Open","High","Low","Close","Volume","symbol"]]

            data.append(stock)

        except Exception as e:

            print(f"Skipping {symbol}: {e}")

            continue

    df = pd.concat(data, ignore_index=True)

    return df