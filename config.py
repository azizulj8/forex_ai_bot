# config.py
# File ini digunakan untuk menyimpan pengaturan bot. JANGAN pernah membagikan file ini jika berisi password akun Live.

# 1. Kredensial MetaTrader 5
MT5_ACCOUNT = 12345678          # Ganti dengan nomor akun Demo Anda
MT5_PASSWORD = "your_password"  # Ganti dengan password akun Demo Anda
MT5_SERVER = "Exness-MT5Trial"  # Ganti dengan nama server broker Anda (tergantung broker)

# 2. Konfigurasi Trading
SYMBOLS = ["XAUUSDm", "EURUSDm", "GBPUSDm"]  # Simbol yang akan ditradingkan
TIMEFRAME_MAIN = "M5"      # Timeframe untuk bot klasik/main (indikator lagging)
TIMEFRAME_MOMENTUM = "M1"  # Timeframe untuk bot momentum scalping (real-time price action)
RISK_PERCENT = 0.01  # Risiko per trade adalah 1% dari total balance akun (Hanya jika USE_FIXED_LOT = False)
RISK_REWARD_RATIO = 2.0  # Risk:Reward ratio = 1:2 (TP dua kali lipat lebih besar dari SL)
SL_PIPS = 30  # Jarak Stop Loss standar dalam pips (Bisa Anda naikkan jika terlalu sering kena SL)
USE_DYNAMIC_SL = True  # Jika True, bot mengabaikan SL_PIPS dan menggunakan volatilitas pasar (ATR)
ATR_SL_MULTIPLIER = 1.2  # Pengali ATR untuk SL. (Contoh: 1.2x rata-rata pergerakan agar SL lebih dekat)
LOOKAHEAD_CANDLES = 30   # Jarak pandang AI ke masa depan untuk target simulasi TP/SL (30 candle)

# 3. Pengaturan Lot (Volume Transaksi)
USE_FIXED_LOT = True      # Set True jika ingin menggunakan lot tetap (konsisten)
FIXED_LOT_SIZE = 0.01      # Ukuran lot tetap (contoh 0.01 atau 0.001 untuk akun cent)

# 3. Path instalasi MT5 di Windows VPS / Parallels
# Jika bot gagal menemukan MT5, uncomment baris di bawah dan sesuaikan jalurnya:
# MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# 4. Pengaturan Pelaporan Telegram
TELEGRAM_BOT_TOKEN = "8616880679:AAHqAtJr_zQsg7P9XhsfHEW4n9Ee9Z-vm2Q"
TELEGRAM_CHAT_ID = "6844797994"
