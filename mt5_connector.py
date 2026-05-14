import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import config

def initialize_mt5():
    """
    Menginisialisasi koneksi ke MetaTrader 5 menggunakan kredensial dari config.py.
    """
    print("Menginisialisasi MetaTrader 5...")
    
    # Inisialisasi MT5
    if not mt5.initialize():
        print("Gagal inisialisasi MT5. Error code:", mt5.last_error())
        return False
    
    # Login ke akun
    authorized = mt5.login(
        config.MT5_ACCOUNT, 
        password=config.MT5_PASSWORD, 
        server=config.MT5_SERVER
    )
    
    if authorized:
        print(f"Berhasil login ke akun: {config.MT5_ACCOUNT}")
        account_info = mt5.account_info()
        if account_info is not None:
            print(f"Saldo saat ini: {account_info.balance} {account_info.currency}")
        return True
    else:
        print(f"Gagal login ke akun {config.MT5_ACCOUNT}. Error code:", mt5.last_error())
        mt5.shutdown()
        return False

def get_historical_data(symbol, timeframe, num_candles):
    """
    Mengambil data historis (candlestick) dari MT5.
    timeframe: misal mt5.TIMEFRAME_M5
    """
    if not mt5.symbol_select(symbol, True):
        print(f"Gagal memilih simbol {symbol}")
        return None
    
    # Dapatkan jumlah candle dari waktu sekarang ke belakang
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    
    if rates is None:
        print(f"Gagal mengambil data untuk {symbol}. Error code:", mt5.last_error())
        return None
        
    # Konversi ke Pandas DataFrame agar mudah diproses AI
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # Jadikan waktu sebagai index
    df.set_index('time', inplace=True)
    
    return df

def close_connection():
    """
    Menutup koneksi MT5 dengan aman.
    """
    mt5.shutdown()
    print("Koneksi MT5 ditutup.")

if __name__ == "__main__":
    # Test koneksi sederhana saat file ini dieksekusi langsung
    if initialize_mt5():
        print("\nMengambil data sampel untuk:", config.SYMBOLS[0])
        # Gunakan TIMEFRAME_M5 sebagai contoh
        df_sample = get_historical_data(config.SYMBOLS[0], mt5.TIMEFRAME_M5, 5)
        if df_sample is not None:
            print(df_sample.tail())
        close_connection()
