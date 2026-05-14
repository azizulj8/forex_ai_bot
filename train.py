import config
import mt5_connector
from data_processor import extract_features
from ai_model import train_and_save_model
import MetaTrader5 as mt5

def main():
    print("--- PROGRAM TRAINING AI TRADING ---")
    
    # 1. Hubungkan Python ke MetaTrader 5 menggunakan login di config.py
    if not mt5_connector.initialize_mt5():
        print("Pastikan aplikasi MetaTrader 5 sedang terbuka dan Anda sudah login ke akun Demo!")
        return

    # Kita uji coba training untuk simbol pertama di config.py (misalnya XAUUSD)
    symbol = config.SYMBOLS[0]
    
    # 2. Ambil data historis (5000 candle terakhir di M5)
    print(f"\n[1] Mengambil 5000 candle masa lalu untuk {symbol}...")
    df = mt5_connector.get_historical_data(symbol, mt5.TIMEFRAME_M5, 5000)
    
    if df is not None and not df.empty:
        # 3. Ekstrak indikator ke dalam data
        print(f"\n[2] Menambahkan indikator teknikal (RSI, MA, MACD) ke dalam data...")
        df_featured = extract_features(df)
        
        # 4. Ajarkan AI dengan data tersebut
        print("\n[3] Memulai pembelajaran (Training) AI...")
        model_filename = f"model_{symbol}.pkl"
        train_and_save_model(df_featured, model_path=model_filename)
        print(f"\nTraining Selesai! Otak AI telah disimpan di file {model_filename}.")
        print("Langkah selanjutnya adalah membuat script Eksekusi Trading yang menggunakan otak ini.")
    else:
        print(f"Gagal mendapatkan data untuk {symbol}. Pastikan nama simbol di config.py sama persis dengan yang ada di Market Watch MT5 (misal jika ada huruf 'm' di belakang, tuliskan dengan 'm' juga, contoh: XAUUSDm).")

    # 5. Putuskan koneksi
    mt5_connector.close_connection()

if __name__ == "__main__":
    main()
