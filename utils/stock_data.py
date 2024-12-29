import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol, period='1y'):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        raise Exception(f"Error fetching stock data: {e}")

def get_key_metrics(info):
    """Extract key financial metrics"""
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

def format_large_number(num):
    """Format large numbers for display"""
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

def calculate_technical_indicators(df):
    """Calculate technical indicators for the stock"""
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df['Close'])
    return df

def calculate_rsi(prices, periods=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
