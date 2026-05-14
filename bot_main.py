import time
import sys

# Memastikan versi Python 3.11+
if sys.version_info < (3, 11):
    print("EROR: Bot ini memerlukan Python versi 3.11 ke atas.")
    print(f"Versi Anda saat ini: {sys.version}")
    sys.exit(1)

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

import config
import mt5_connector
from data_processor import extract_features
from ai_model import load_model
from executor import execute_trade_signal
from reporter import generate_daily_report, send_telegram_message

def run_bot():
    print("========================================")
    print("   MEMULAI LIVE AI TRADING BOT FOREX    ")
    print("========================================")
    
    # 1. Koneksi ke Broker (Exness/MT5)
    if not mt5_connector.initialize_mt5():
        return

    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME_MAIN, mt5.TIMEFRAME_M5)

    models = {}
    last_candle_times = {}
    
    # 2. Muat Otak AI dari harddisk
    for symbol in config.SYMBOLS:
        model_filename = f"model_{symbol}.pkl"
        ai_model = load_model(model_filename)
        if ai_model is not None:
            models[symbol] = ai_model
            last_candle_times[symbol] = None
            print(f"Model AI {symbol} berhasil dimuat.")
        else:
            print(f"Peringatan: Model untuk {symbol} tidak ditemukan. Simbol ini akan dilewati.")
            
    if not models:
        print("Bot dihentikan karena tidak ada model AI satupun yang termuat. Jalankan train.py terlebih dahulu!")
        mt5_connector.close_connection()
        return
        
    print(f"\nBot siap mengawasi pasar di timeframe {config.TIMEFRAME_MAIN}...")
    print("Tekan Ctrl+C untuk menghentikan bot.")
    
    report_sent = False

    try:
        # 3. Loop utama bot (Berjalan tanpa henti)
        while True:
            for symbol, ai_model in models.items():
                # HOT-SWAP: Cek apakah ada update model baru di disk
                model_filename = f"model_{symbol}.pkl"
                try:
                    current_mtime = os.path.getmtime(model_filename)
                    if not hasattr(ai_model, 'last_mtime'):
                        ai_model.last_mtime = current_mtime
                    elif current_mtime > ai_model.last_mtime:
                        print(f"[{symbol}] Deteksi update model baru! Memuat ulang otak...")
                        new_model = load_model(model_filename)
                        if new_model:
                            models[symbol] = new_model
                            models[symbol].last_mtime = current_mtime
                except:
                    pass

                # Mengambil 100 candle terbaru untuk kalkulasi indikator
                df = mt5_connector.get_historical_data(symbol, mt5_tf, 100)
                if df is None or df.empty:
                    continue
                    
                # Kita fokus menganalisis saat sebuah candle baru saja ditutup
                current_candle_time = df.index[-1]
                
                if last_candle_times[symbol] is None:
                    last_candle_times[symbol] = current_candle_time
                    print(f"[{symbol}] Menunggu penutupan candle berikutnya...")
                
                # Jika waktu candle bergeser, berarti candle sebelumnya sudah tutup (fixed)
                elif current_candle_time > last_candle_times[symbol]:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [{symbol}] Candle baru terdeteksi! Meminta AI menganalisa...")
                    last_candle_times[symbol] = current_candle_time
                    
                    # Olah data harga menjadi indikator teknikal
                    df_features = extract_features(df)
                    
                    if not df_features.empty:
                        # Ambil baris data yang paling terakhir
                        latest_data = df_features.iloc[-1:]
                        
                        feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                                        'body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                                        'double_top', 'double_bottom']
                        
                        # 4. Minta Prediksi dari AI
                        prediction = ai_model.predict(latest_data[feature_cols])[0]
                        
                        if prediction == 0:
                            print(f"[{symbol}] Sinyal: NEUTRAL/HOLD (Probabilitas SL tinggi). Skip.")
                            continue
                            
                        is_buy_signal = (prediction == 1)
                        signal_text = "BUY" if is_buy_signal else "SELL"
                        print(f"[{symbol}] Sinyal AI Terdeteksi: {signal_text}")
                        
                        # 5. Filter Manajemen Posisi
                        positions = mt5.positions_get(symbol=symbol)
                        max_positions = getattr(config, 'MAX_POSITIONS_PER_SYMBOL', 5)
                        
                        if positions is None or len(positions) < max_positions:
                            current_atr = latest_data['ATR'].iloc[0]
                            # Kirim fitur yang digunakan AI ke executor agar dicatat ke DB
                            features_dict = latest_data[feature_cols].iloc[0].to_dict()
                            execute_trade_signal(symbol, is_buy_signal, sl_pips=config.SL_PIPS, 
                                               current_atr=current_atr, features_dict=features_dict, bot_type="MAIN")
                        else:
                            print(f"Batas maksimal {max_positions} posisi tercapai untuk {symbol}. Abaikan sinyal.")

                        
            # Jadwal Rapor Harian: Cek apakah jam 23:55
            current_time = datetime.now()
            if current_time.hour == 23 and current_time.minute == 55 and not report_sent:
                print("\n[JADWAL] Mengirim Rapor Harian ke Telegram...")
                report_text = generate_daily_report()
                if report_text:
                    send_telegram_message(report_text)
                report_sent = True
            # Reset status terkirim pada jam 00:00 (hari berganti)
            elif current_time.hour == 0:
                report_sent = False

            # Tunggu 5 detik sebelum mengecek data harga lagi agar CPU tidak terbebani
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nBot dimatikan secara paksa oleh Anda.")
    finally:
        mt5_connector.close_connection()

if __name__ == "__main__":
    run_bot()
