import pandas as pd
import numpy as np
import config

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

def calculate_atr(data, period=14):
    """Menghitung Average True Range (ATR) untuk mendeteksi volatilitas harga"""
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    atr = true_range.rolling(window=period).mean()
    return atr

def generate_smart_targets(df, lookahead=12):
    """
    Mensimulasikan setiap baris data untuk melihat apakah TP akan tersentuh duluan sebelum SL.
    Target: 1 (Buy untung), 2 (Sell untung), 0 (Neutral/SL duluan).
    """
    targets = np.zeros(len(df))
    
    # Dapatkan parameter dari config
    sl_multiplier = getattr(config, 'ATR_SL_MULTIPLIER', 1.5)
    tp_multiplier = sl_multiplier * getattr(config, 'RISK_REWARD_RATIO', 2.0)
    
    # Konversi ke numpy untuk kecepatan proses
    closes = df['close'].values
    highs = df['high'].values
    lows = df['low'].values
    atrs = df['ATR'].values
    
    for i in range(len(df) - lookahead):
        price_entry = closes[i]
        atr = atrs[i]
        
        # Jarak harga (bukan pips)
        sl_dist = atr * sl_multiplier
        tp_dist = atr * tp_multiplier
        
        # Ambil jendela masa depan
        future_highs = highs[i+1 : i+1+lookahead]
        future_lows = lows[i+1 : i+1+lookahead]
        
        buy_win = False
        sell_win = False
        
        # Simulasi BUY
        for j in range(len(future_highs)):
            if future_lows[j] <= (price_entry - sl_dist):
                break # Kena SL
            if future_highs[j] >= (price_entry + tp_dist):
                buy_win = True
                break # Kena TP
                
        # Simulasi SELL
        for j in range(len(future_highs)):
            if future_highs[j] >= (price_entry + sl_dist):
                break # Kena SL
            if future_lows[j] <= (price_entry - tp_dist):
                sell_win = True
                break # Kena TP
                
        if buy_win and not sell_win:
            targets[i] = 1
        elif sell_win and not buy_win:
            targets[i] = 2
            
    df['smart_target'] = targets
    return df

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
    
    # ATR (Average True Range)
    df['ATR'] = calculate_atr(df, period=14)
    
    # Fitur pergerakan harga dasar
    df['body_size'] = df['close'] - df['open']
    df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
    
    # Target prediksi (Smart Simulation)
    # 1: Buy Success, 2: Sell Success, 0: Neutral/Loss
    df = generate_smart_targets(df, lookahead=12)
    
    # Hapus baris yang mengandung NaN
    df.dropna(inplace=True)
    
    return df
