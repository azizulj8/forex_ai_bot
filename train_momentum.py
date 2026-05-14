import config
import mt5_connector
from data_processor_momentum import extract_features
from ai_model_momentum import train_and_save_model
import sys
import MetaTrader5 as mt5

if sys.version_info < (3, 11):
    print("EROR: Script training ini memerlukan Python versi 3.11 ke atas.")
    sys.exit(1)

def main():
    print("--- PROGRAM TRAINING AI MOMENTUM ---")
    
    if not mt5_connector.initialize_mt5():
        return

    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME_MOMENTUM, mt5.TIMEFRAME_M1)

    for symbol in config.SYMBOLS:
        print(f"\n=========================================")
        print(f"   MEMULAI TRAINING MOMENTUM: {symbol}")
        print(f"=========================================")
        
        df = mt5_connector.get_historical_data(symbol, mt5_tf, 5000)
        
        if df is not None and not df.empty:
            print(f"\n[2] Mengekstrak fitur momentum murni...")
            df_featured = extract_features(df)
            
            print("\n[3] Memulai pembelajaran AI Momentum...")
            model_filename = f"model_momentum_{symbol}.pkl"
            train_and_save_model(df_featured, model_path=model_filename)
            print(f"\nTraining Selesai! Otak AI Momentum disimpan di {model_filename}.")
        else:
            print(f"Gagal mendapatkan data untuk {symbol}.")

    mt5_connector.close_connection()

if __name__ == "__main__":
    main()
