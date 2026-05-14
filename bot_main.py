import time
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

    symbol = config.SYMBOLS[0]  # Fokus ke satu mata uang dulu (misal XAUUSD)
    
    # 2. Muat Otak AI dari harddisk
    model_filename = f"model_{symbol}.pkl"
    ai_model = load_model(model_filename)
    if ai_model is None:
        print("Bot dihentikan karena tidak ada model AI. Jalankan train.py terlebih dahulu!")
        mt5_connector.close_connection()
        return
        
    print(f"Model AI berhasil dimuat. Bot siap mengawasi {symbol} di {config.TIMEFRAME}...")
    print("Tekan Ctrl+C untuk menghentikan bot.")
    
    last_candle_time = None
    report_sent = False

    try:
        # 3. Loop utama bot (Berjalan tanpa henti)
        while True:
            # Mengambil 100 candle terbaru untuk kalkulasi indikator
            df = mt5_connector.get_historical_data(symbol, mt5.TIMEFRAME_M5, 100)
            if df is None or df.empty:
                time.sleep(5)
                continue
                
            # Kita fokus menganalisis saat sebuah candle 5 Menit (M5) baru saja ditutup
            current_candle_time = df.index[-1]
            
            if last_candle_time is None:
                last_candle_time = current_candle_time
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Menunggu penutupan candle 5 Menit berikutnya...")
            
            # Jika waktu candle bergeser, berarti candle sebelumnya sudah tutup (fixed)
            elif current_candle_time > last_candle_time:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Candle baru terdeteksi! Meminta AI menganalisa pasar...")
                last_candle_time = current_candle_time
                
                # Olah data harga menjadi indikator teknikal
                df_features = extract_features(df)
                
                if not df_features.empty:
                    # Ambil baris data yang paling terakhir (candle yang baru saja tutup)
                    latest_data = df_features.iloc[-1:]
                    
                    # Kolom yang dikenali AI
                    feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                                    'body_size', 'upper_shadow', 'lower_shadow', 'ATR']
                    
                    # 4. Minta Prediksi dari AI
                    prediction = ai_model.predict(latest_data[feature_cols])[0]
                    is_buy_signal = (prediction == 1)
                    
                    if is_buy_signal:
                        print(">> PREDIKSI AI: HARGA AKAN NAIK (Sinyal BUY)")
                    else:
                        print(">> PREDIKSI AI: HARGA AKAN TURUN (Sinyal SELL)")
                    
                    # 5. Filter Manajemen Posisi
                    # Bot ini tidak akan membuka posisi baru jika masih ada posisi yang belum menyentuh TP/SL
                    positions = mt5.positions_get(symbol=symbol)
                    
                    if positions is None or len(positions) == 0:
                        # Tidak ada posisi terbuka, eksekusi sinyal!
                        current_atr = latest_data['ATR'].iloc[0]
                        execute_trade_signal(symbol, is_buy_signal, sl_pips=config.SL_PIPS, current_atr=current_atr)
                    else:
                        print("Abaikan sinyal: Masih ada posisi yang sedang berjalan/terbuka. Bot menunggu TP atau SL tersentuh.")
                        
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
