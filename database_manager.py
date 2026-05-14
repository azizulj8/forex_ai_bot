import sqlite3
import json
import os
from datetime import datetime

DB_NAME = "trading_history.db"

def init_db():
    """Menginisialisasi database dan tabel jika belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel trades untuk merekam posisi yang dibuka
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            type TEXT, -- 'BUY' atau 'SELL'
            open_price REAL,
            sl REAL,
            tp REAL,
            open_time TIMESTAMP,
            close_price REAL,
            close_time TIMESTAMP,
            profit REAL,
            status TEXT, -- 'OPEN', 'TP', 'SL', 'CLOSED'
            features_json TEXT, -- Data indikator saat trade dibuka (JSON)
            bot_type TEXT -- 'MAIN' atau 'MOMENTUM'
        )
    ''')
    
    conn.commit()
    conn.close()

def save_open_trade(symbol, trade_type, open_price, sl, tp, features_dict, bot_type="MAIN"):
    """Mencatat pembukaan posisi baru."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    features_json = json.dumps(features_dict)
    open_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO trades (symbol, type, open_price, sl, tp, open_time, status, features_json, bot_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (symbol, trade_type, open_price, sl, tp, open_time, 'OPEN', features_json, bot_type))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trade_id

def update_closed_trades(mt5_history):
    """
    Mengupdate status trade di database berdasarkan data history dari MT5.
    mt5_history: list of positions/deals dari mt5.history_deals_get
    """
    if not mt5_history:
        return
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for deal in mt5_history:
        # Cari trade di DB yang symbol-nya sama dan statusnya masih OPEN
        # Kita gunakan logika pencocokan waktu atau harga jika diperlukan, 
        # namun untuk awalan kita cari yang open_price-nya mendekati
        
        # Cari trade yang belum ditutup
        cursor.execute("SELECT id FROM trades WHERE symbol = ? AND status = 'OPEN' AND type = ?", 
                       (deal.symbol, 'BUY' if deal.type == 0 else 'SELL'))
        row = cursor.fetchone()
        
        if row:
            trade_id = row[0]
            close_time = datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d %H:%M:%S')
            profit = deal.profit
            status = 'TP' if profit > 0 else 'SL'
            
            cursor.execute('''
                UPDATE trades 
                SET close_price = ?, close_time = ?, profit = ?, status = ?
                WHERE id = ?
            ''', (deal.price, close_time, profit, status, trade_id))
            
    conn.commit()
    conn.close()

def get_recent_training_data(days=30):
    """Mengambil data trade terakhir untuk bahan retraining AI."""
    conn = sqlite3.connect(DB_NAME)
    # Gunakan row_factory agar hasil query bisa diakses seperti dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trades 
        WHERE status != 'OPEN' 
        AND open_time >= date('now', ?)
    ''', (f'-{days} days',))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Database trading_history.db berhasil diinisialisasi.")
