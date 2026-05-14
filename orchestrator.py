import schedule
import time
import subprocess
import os
from datetime import datetime
import MetaTrader5 as mt5
import config
import mt5_connector
import database_manager

def daily_maintenance():
    """
    Fungsi yang dijalankan setiap tengah malam untuk:
    1. Mengupdate sejarah trade dari MT5 ke DB lokal.
    2. Menjalankan proses Re-Training AI.
    3. Mengevaluasi apakah model baru lebih baik.
    """
    print(f"\n[{datetime.now()}] Memulai pemeliharaan harian (Daily MLOps Pipeline)...")
    
    # 1. Update DB dari MT5 History
    if mt5_connector.initialize_mt5():
        # Ambil history 24 jam terakhir
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        history_deals = mt5.history_deals_get(from_date, datetime.now())
        if history_deals:
            database_manager.update_closed_trades(history_deals)
            print(f"Berhasil mengupdate {len(history_deals)} data transaksi ke database.")
        mt5_connector.close_connection()

    # 2. Jalankan Training Ulang (Parallel)
    print("Menjalankan Training ulang untuk bot Main dan Momentum...")
    try:
        subprocess.run(["python3", "train.py"], check=True)
        subprocess.run(["python3", "train_momentum.py"], check=True)
        print("Proses Re-Training selesai.")
    except Exception as e:
        print(f"Gagal menjalankan re-training: {e}")

    # 3. Model Evaluation (A/B Testing)
    print("Mengevaluasi apakah model baru lebih baik dari model yang sedang berjalan...")
    import model_evaluator
    for symbol in config.SYMBOLS:
        # Evaluasi bot Main
        main_upgraded = model_evaluator.evaluate_model(symbol, "MAIN")
        # Evaluasi bot Momentum
        momentum_upgraded = model_evaluator.evaluate_model(symbol, "MOMENTUM")
        
        if main_upgraded or momentum_upgraded:
            print(f"[{symbol}] Deteksi update model baru. Bot akan memuat ulang otak di siklus berikutnya.")
    
    print(f"[{datetime.now()}] Seluruh proses pemeliharaan selesai.")

def start_orchestrator():
    print("Orchestrator AI DevOps aktif. Menunggu jadwal pemeliharaan (Jam 00:05)...")
    
    # Jadwalkan setiap hari jam 00:05
    schedule.every().day.at("00:05").do(daily_maintenance)
    
    # Tambahan: Update DB setiap 1 jam agar data tetap segar
    schedule.every().hour.do(daily_maintenance) # Sementara kita jalankan setiap jam untuk testing
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    database_manager.init_db()
    start_orchestrator()
