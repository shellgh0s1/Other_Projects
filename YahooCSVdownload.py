import requests
import time
import datetime
import os
import random
from fetch_sp500_tickers import fetch_sp500_tickers
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_timestamps():
    """Calculates start and end timestamps for a 5-year period."""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=5*365)
    start_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day)
    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(time.time())
    return start_timestamp, end_timestamp

def download_historical_data(ticker, save_dir="CSV_FILES"):
    """
    Downloads historical price data for a stock and saves it as a CSV file.

    Args:
        ticker (str): The ticker symbol of the stock.
        save_dir (str, optional): The directory to save the downloaded CSV file. Defaults to "CSV_FILES".
    """
    base_url = "https://query1.finance.yahoo.com/v7/finance/download/"
    start_timestamp, end_timestamp = calculate_timestamps()
    url = f"{base_url}{ticker}?period1={start_timestamp}&period2={end_timestamp}&interval=1mo&events=history&includeAdjustedClose=true"

    delay = 30  # Initial delay in seconds
    max_delay = 600  # Maximum delay

    for attempt in range(5):  # Increase maximum retry attempts
        try:
            response = requests.get(url, headers={'User-Agent': 'Your_User_Agent'})
            response.raise_for_status()  # Raise exception for non-200 status codes

            os.makedirs(save_dir, exist_ok=True)
            filename = f"{ticker}.csv"
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)

            logging.info(f"Downloaded historical data for {ticker} to {filepath}")
            return  # Exit the function on success
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 429:
                logging.warning(f"Error downloading data for {ticker}: Too Many Requests. Retrying in {delay} seconds...")
                time.sleep(delay + random.uniform(0, delay))
                delay = min(delay * 2, max_delay)  # Exponential backoff with random jitter
            else:
                logging.error(f"Error downloading data for {ticker}: {e}")

# Track failed downloads
failed_tickers = []

# Download data for all S&P 500 tickers
if __name__ == "__main__":
    tickers = fetch_sp500_tickers()

    for ticker in tickers:
        try:
            download_historical_data(ticker)
        except Exception as e:
            logging.error(f"Failed to download data for {ticker}: {e}")
            failed_tickers.append(ticker)

    # Save failed tickers to a text file
    with open("failed_tickers.txt", "w") as f:
        for ticker in failed_tickers:
            f.write(ticker + "\n")
