import pandas as pd
import numpy as np
import config
from data_processor import calculate_atr, generate_smart_targets

def extract_features(df):
    """
    Ekstrak fitur khusus momentum tanpa lagging indicators.
    Fokus pada kekuatan candle real-time.
    """
    df = df.sort_index()
    
    # ATR tetap diperlukan untuk perhitungan SL dinamis
    df['ATR'] = calculate_atr(df, period=14)
    
    # 1. Fitur pergerakan harga dasar
    df['body_size'] = df['close'] - df['open']
    df['abs_body_size'] = np.abs(df['body_size'])
    df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
    
    # 2. Fitur Momentum Surge (Besaran candle dibanding rata-rata masa lalu)
    avg_body = df['abs_body_size'].rolling(window=10).mean().shift(1)
    avg_body = avg_body.replace(0, np.nan) # Hindari error division by zero
    df['momentum_surge'] = df['abs_body_size'] / avg_body
    df['momentum_surge'] = df['momentum_surge'].fillna(0)
    
    # 3. Wick to Body Ratio (Semakin kecil sumbu, semakin utuh momentumnya)
    total_shadow = df['upper_shadow'] + df['lower_shadow']
    df['wick_ratio'] = total_shadow / (df['abs_body_size'] + 0.00001)
    
    # 4. Deteksi Pola Engulfing Kuat
    prev_body_size = df['body_size'].shift(1)
    prev_open = df['open'].shift(1)
    prev_close = df['close'].shift(1)
    
    is_bullish_engulfing = (prev_body_size < 0) & (df['body_size'] > 0) & (df['close'] > prev_open) & (df['open'] <= prev_close)
    is_bearish_engulfing = (prev_body_size > 0) & (df['body_size'] < 0) & (df['close'] < prev_open) & (df['open'] >= prev_close)
    
    df['is_bullish_engulfing'] = is_bullish_engulfing.astype(int)
    df['is_bearish_engulfing'] = is_bearish_engulfing.astype(int)
    
    # 5. Streak Arah (Berapa candle warna sama secara beruntun)
    # 1 jika hijau, -1 jika merah
    direction = np.where(df['body_size'] > 0, 1, np.where(df['body_size'] < 0, -1, 0))
    # Hitung streak beruntun
    streak_mask = (direction != np.roll(direction, 1))
    df['direction_streak'] = df.groupby(streak_mask.cumsum()).cumcount() + 1
    df['direction_streak'] = df['direction_streak'] * direction # (+) untuk rentetan hijau, (-) untuk merah
    
    # Target prediksi (Smart Simulation)
    df = generate_smart_targets(df)
    
    # Bersihkan NaN
    df.dropna(inplace=True)
    
    return df
