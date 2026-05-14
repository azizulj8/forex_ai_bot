import MetaTrader5 as mt5
from datetime import datetime, time as datetime_time
import requests
import config
import mt5_connector

def send_telegram_message(message):
    """Mengirim pesan (rapor) ke Telegram Anda menggunakan Bot API."""
    token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    if not token or not chat_id or token == "MASUKKAN_TOKEN_BOT_ANDA_DISINI":
        print("Pengaturan Telegram belum diisi di config.py! Laporan batal dikirim.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Laporan berhasil dikirim ke Telegram Anda!")
            return True
        else:
            print(f"Gagal mengirim Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"Error saat mengirim ke Telegram: {e}")
        return False

def generate_daily_report():
    """Menghitung transaksi bot hari ini dari server MT5."""
    now = datetime.now()
    start_of_day = datetime.combine(now.date(), datetime_time.min)
    
    # Ambil riwayat Deals (transaksi selesai) dari jam 00:00 hari ini sampai detik ini
    deals = mt5.history_deals_get(start_of_day, now)
    
    if deals is None:
        print("Gagal mengambil riwayat transaksi. Error:", mt5.last_error())
        return None
        
    total_trades = 0
    total_profit_usd = 0.0
    win_count = 0
    loss_count = 0
    
    # Harus sesuai dengan Magic Number di executor.py
    BOT_MAGIC_NUMBER = 999111
    
    for deal in deals:
        # Hanya ambil transaksi OUT (ditutup) yang dilakukan oleh Bot kita (bukan manual)
        if deal.entry == mt5.DEAL_ENTRY_OUT and deal.magic == BOT_MAGIC_NUMBER:
            total_trades += 1
            total_profit_usd += deal.profit
            
            # Jika profit lebih besar dari 0, berarti Win (kena Take Profit)
            if deal.profit > 0:
                win_count += 1
            # Jika profit kurang dari 0, berarti Loss (kena Stop Loss)
            elif deal.profit < 0:
                loss_count += 1
                
    if total_trades > 0:
        win_rate = (win_count / total_trades) * 100
    else:
        win_rate = 0.0
        
    # Format laporan Telegram
    report = f"📊 <b>RAPOR HARIAN AI BOT</b> 📊\n"
    report += f"📅 Tanggal: {now.strftime('%d-%m-%Y')}\n\n"
    report += f"Total Transaksi: <b>{total_trades}</b>\n"
    report += f"✅ Kena TP (Win): {win_count}\n"
    report += f"❌ Kena SL (Loss): {loss_count}\n"
    report += f"🎯 Win Rate: <b>{win_rate:.1f}%</b>\n"
    report += f"💰 Total PnL: <b>${total_profit_usd:.2f}</b>\n\n"
    report += f"🤖 <i>Laporan dikirim otomatis oleh AI Forex Bot Anda.</i>"
    
    return report

if __name__ == "__main__":
    # Ini jika Anda ingin mentes file rapor secara manual
    if mt5_connector.initialize_mt5():
        print("Membuat laporan harian...")
        report_text = generate_daily_report()
        
        if report_text:
            print("\n" + report_text)
            send_telegram_message(report_text)
            
        mt5_connector.close_connection()
