# config.py
# File ini digunakan untuk menyimpan pengaturan bot. JANGAN pernah membagikan file ini jika berisi password akun Live.

# 1. Kredensial MetaTrader 5
MT5_ACCOUNT = 12345678          # Ganti dengan nomor akun Demo Anda
MT5_PASSWORD = "your_password"  # Ganti dengan password akun Demo Anda
MT5_SERVER = "Exness-MT5Trial"  # Ganti dengan nama server broker Anda (tergantung broker)

# 2. Konfigurasi Trading
SYMBOLS = ["XAUUSDm", "EURUSDm", "GBPUSDm"]  # Simbol yang akan ditradingkan (Exness sering menambahkan 'm' di akhir untuk akun Standard, atau tanpa huruf untuk Raw)
TIMEFRAME = "M5"  # Timeframe untuk scalping (M1 atau M5)
RISK_PERCENT = 0.01  # Risiko per trade adalah 1% dari total balance akun
RISK_REWARD_RATIO = 2.0  # Risk:Reward ratio = 1:2 (TP dua kali lipat lebih besar dari SL)
SL_PIPS = 30  # Jarak Stop Loss standar dalam pips (Bisa Anda naikkan jika terlalu sering kena SL)

# 3. Path instalasi MT5 di Windows VPS / Parallels
# Jika bot gagal menemukan MT5, uncomment baris di bawah dan sesuaikan jalurnya:
# MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# 4. Pengaturan Pelaporan Telegram
TELEGRAM_BOT_TOKEN = "8616880679:AAHqAtJr_zQsg7P9XhsfHEW4n9Ee9Z-vm2Q"
TELEGRAM_CHAT_ID = "6844797994"
