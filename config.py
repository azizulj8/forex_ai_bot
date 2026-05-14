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
RISK_REWARD_RATIO = 1.5  # Rasio lebih realistis untuk scalping (1:1.5)
SL_PIPS = 10              # Stop Loss cuma 10 pips (Scalping ketat)
USE_DYNAMIC_SL = True     
ATR_SL_MULTIPLIER = 1.0   # SL mengikuti volatilitas tapi tidak terlalu lebar
LOOKAHEAD_CANDLES = 15    # AI hanya memprediksi nasib trade dalam 15 menit ke depan (M1)

# 3. Pengaturan Lot (Volume Transaksi)
USE_FIXED_LOT = True      # Set True jika ingin menggunakan lot tetap (konsisten)
FIXED_LOT_SIZE = 0.01      # Ukuran lot tetap (contoh 0.01 atau 0.001 untuk akun cent)
MAX_POSITIONS_PER_SYMBOL = 5  # Maksimal posisi terbuka bersamaan untuk satu mata uang
CONFIDENCE_THRESHOLD = 0.8  # Tingkat keyakinan AI (0.8 = 80%) untuk mengeksekusi sinyal (Abaikan jika di bawah ini)

# 3. Path instalasi MT5 di Windows VPS / Parallels
# Jika bot gagal menemukan MT5, uncomment baris di bawah dan sesuaikan jalurnya:
# MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# 4. Pengaturan Pelaporan Telegram
TELEGRAM_BOT_TOKEN = "8616880679:AAHqAtJr_zQsg7P9XhsfHEW4n9Ee9Z-vm2Q"
TELEGRAM_CHAT_ID = "6844797994"
