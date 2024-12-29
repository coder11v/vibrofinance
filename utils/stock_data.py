import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_stock_data(symbol, period='1y'):
    """Fetch stock data from Yahoo Finance"""
    try:
        logger.info(f"Fetching data for symbol: {symbol}")
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        logger.info(f"Successfully fetched data for {symbol}")
        return hist, info
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        raise Exception(f"Error fetching stock data for {symbol}: {str(e)}")

def get_multiple_stocks_data(symbols, period='1y'):
    """Fetch data for multiple stocks"""
    try:
        logger.info(f"Fetching data for multiple symbols: {symbols}")
        data = {}
        for symbol in symbols:
            try:
                hist, info = get_stock_data(symbol, period)
                data[symbol] = {
                    'history': hist,
                    'info': info
                }
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue

        if not data:
            raise Exception("Failed to fetch data for all requested symbols")
        return data
    except Exception as e:
        logger.error(f"Error in get_multiple_stocks_data: {str(e)}")
        raise Exception(f"Error fetching multiple stocks data: {str(e)}")

def get_key_metrics(info):
    """Extract key financial metrics"""
    try:
        metrics = {
            'Market Cap': info.get('marketCap', 'N/A'),
            'PE Ratio': info.get('trailingPE', 'N/A'),
            'EPS': info.get('trailingEps', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Volume': info.get('volume', 'N/A'),
        }
        return metrics
    except Exception as e:
        logger.error(f"Error extracting metrics: {str(e)}")
        return {metric: 'N/A' for metric in ['Market Cap', 'PE Ratio', 'EPS', '52 Week High', '52 Week Low', 'Dividend Yield', 'Volume']}

def format_large_number(num):
    """Format large numbers for display"""
    try:
        if not isinstance(num, (int, float)) or pd.isna(num):
            return 'N/A'

        if num >= 1e12:
            return f'${num/1e12:.2f}T'
        elif num >= 1e9:
            return f'${num/1e9:.2f}B'
        elif num >= 1e6:
            return f'${num/1e6:.2f}M'
        else:
            return f'${num:,.2f}'
    except Exception as e:
        logger.error(f"Error formatting number: {str(e)}")
        return 'N/A'

def calculate_technical_indicators(df):
    """Calculate technical indicators for the stock"""
    try:
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = calculate_rsi(df['Close'])
        return df
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        raise Exception(f"Error calculating technical indicators: {str(e)}")

def calculate_rsi(prices, periods=14):
    """Calculate Relative Strength Index"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        logger.error(f"Error calculating RSI: {str(e)}")
        raise Exception(f"Error calculating RSI: {str(e)}")

def normalize_stock_prices(df):
    """Normalize stock prices to start from 100 for comparison"""
    try:
        return (df['Close'] / df['Close'].iloc[0]) * 100
    except Exception as e:
        logger.error(f"Error normalizing stock prices: {str(e)}")
        raise Exception(f"Error normalizing stock prices: {str(e)}")