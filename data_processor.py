import pandas as pd
import numpy as np

def calculate_rsi(data, period=14):
    """Menghitung Relative Strength Index (RSI)"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    """Menghitung Moving Average Convergence Divergence (MACD)"""
    short_ema = data['close'].ewm(span=short_period, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_period, adjust=False).mean()
    
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal

def extract_features(df):
    """
    Menambahkan indikator teknikal ke dalam DataFrame harga sebagai fitur untuk AI.
    Menghapus baris yang memiliki nilai NaN di awal karena perhitungan MA/RSI.
    """
    # Pastikan data terurut berdasarkan waktu
    df = df.sort_index()
    
    # Simple Moving Averages (SMA)
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    
    # RSI
    df['RSI'] = calculate_rsi(df, period=14)
    
    # MACD
    df['MACD'], df['MACD_Signal'] = calculate_macd(df)
    
    # Fitur pergerakan harga dasar
    df['body_size'] = df['close'] - df['open']
    df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
    
    # Target prediksi (Supervised Learning)
    # 1 jika harga close candle BERIKUTNYA lebih tinggi (Buy), 0 jika turun (Sell)
    # Ini untuk melatih model memprediksi arah candle selanjutnya
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # Hapus baris yang mengandung NaN (karena rolling window/shift)
    df.dropna(inplace=True)
    
    return df
