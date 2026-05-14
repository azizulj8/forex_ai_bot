import time
import sys
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

if sys.version_info < (3, 11):
    print("EROR: Bot ini memerlukan Python versi 3.11 ke atas.")
    sys.exit(1)

import config
import mt5_connector
from data_processor_momentum import extract_features
from ai_model_momentum import load_model
from executor import execute_trade_signal
from reporter import generate_daily_report, send_telegram_message

def run_bot():
    print("========================================")
    print("   MEMULAI LIVE AI MOMENTUM SCALPER     ")
    print("========================================")
    
    if not mt5_connector.initialize_mt5():
        return

    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME, mt5.TIMEFRAME_M1)

    models = {}
    last_candle_times = {}
    
    for symbol in config.SYMBOLS:
        model_filename = f"model_momentum_{symbol}.pkl"
        ai_model = load_model(model_filename)
        if ai_model is not None:
            models[symbol] = ai_model
            last_candle_times[symbol] = None
            print(f"Model Momentum {symbol} berhasil dimuat.")
        else:
            print(f"Model {model_filename} tidak ditemukan. Lewati {symbol}.")
            
    if not models:
        print("Bot dihentikan: Tidak ada model AI momentum. Jalankan train_momentum.py!")
        mt5_connector.close_connection()
        return
        
    print(f"\nBot Momentum siap mengawasi pasar di timeframe {config.TIMEFRAME}...")
    report_sent = False

    try:
        while True:
            for symbol, ai_model in models.items():
                df = mt5_connector.get_historical_data(symbol, mt5_tf, 100)
                if df is None or df.empty:
                    continue
                    
                current_candle_time = df.index[-1]
                
                if last_candle_times[symbol] is None:
                    last_candle_times[symbol] = current_candle_time
                    print(f"[{symbol}] Menunggu penutupan candle...")
                
                elif current_candle_time > last_candle_times[symbol]:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [{symbol}] Candle ditutup! Mengukur momentum...")
                    last_candle_times[symbol] = current_candle_time
                    
                    df_features = extract_features(df)
                    
                    if not df_features.empty:
                        latest_data = df_features.iloc[-1:]
                        
                        feature_cols = ['body_size', 'abs_body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                                        'momentum_surge', 'wick_ratio', 'is_bullish_engulfing', 
                                        'is_bearish_engulfing', 'direction_streak']
                        
                        prediction = ai_model.predict(latest_data[feature_cols])[0]
                        
                        if prediction == 0:
                            print(f"[{symbol}] Momentum LEMAH / Berisiko. HOLD.")
                            continue
                            
                        is_buy_signal = (prediction == 1)
                        signal_text = "BUY" if is_buy_signal else "SELL"
                        print(f"[{symbol}] 🔥 MOMENTUM TERDETEKSI: {signal_text} 🔥")
                        
                        positions = mt5.positions_get(symbol=symbol)
                        
                        if positions is None or len(positions) == 0:
                            current_atr = latest_data['ATR'].iloc[0]
                            execute_trade_signal(symbol, is_buy_signal, sl_pips=config.SL_PIPS, current_atr=current_atr)
                        else:
                            print(f"Abaikan {signal_text}: Masih ada posisi terbuka di {symbol}.")
                        
            current_time = datetime.now()
            if current_time.hour == 23 and current_time.minute == 55 and not report_sent:
                report_text = generate_daily_report()
                if report_text:
                    send_telegram_message(report_text)
                report_sent = True
            elif current_time.hour == 0:
                report_sent = False

            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nBot dimatikan secara paksa.")
    finally:
        mt5_connector.close_connection()

if __name__ == "__main__":
    run_bot()
