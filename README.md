# Forex AI Trading Bot

Sistem *Automated Trading* (Robot Trading) berbasis Artificial Intelligence (AI) untuk pasar Forex. Bot ini menggunakan *Machine Learning* (Random Forest dengan Auto-Tuning GridSearchCV) untuk memprediksi arah pergerakan harga (*candlestick*) dan mengeksekusi order Buy/Sell secara otomatis melalui platform MetaTrader 5 (MT5).

## Fitur Utama
1. **Prediksi Cerdas:** Mengekstrak indikator teknikal (SMA, RSI, MACD) secara *real-time* dan meminta AI untuk memprediksi probabilitas tren pasar.
2. **Self-Adjusting Logic:** AI tidak menggunakan logika baku, melainkan secara otomatis mencari konfigurasi *hyperparameter* terbaiknya sendiri untuk mencegah bias.
3. **Automated Money Management:** Ukuran Lot dihitung otomatis sesuai saldo akun, mempertahankan batas risiko tetap (misal 1% per posisi).
4. **Disiplin Risk 1:2:** Stop Loss dan Take Profit akan selalu dipasang secara konsisten dengan perbandingan Risk:Reward 1:2.
5. **Rapor Harian Telegram:** Menghitung jumlah transaksi, Win Rate, dan Profit setiap tengah malam, lalu mengirim laporannya ke Telegram Anda.
6. **Backtester Simulator:** Anda dapat mem-backtest logika AI menggunakan data puluhan ribu *candle* untuk melihat kalkulasi simulasi profit/loss dalam dolar.

## Persyaratan Sistem (Requirements)
- **Sistem Operasi:** Windows (Wajib, karena *library* `MetaTrader5` Python hanya berjalan di Windows secara natively. Jika Anda menggunakan Mac, gunakan VPS Windows atau Virtual Machine seperti Parallels).
- **Aplikasi:** MetaTrader 5 Terminal terinstal dan terhubung ke akun broker Anda (contoh: Exness, IC Markets).
- **Python:** Versi 3.11 ke atas (Disarankan 3.12+).
- **Library:** 
  - `MetaTrader5`
  - `pandas`
  - `scikit-learn`
  - `numpy`
  - `requests`

## Cara Instalasi
1. *Clone* repositori ini ke dalam komputer/VPS Windows Anda.
2. Buka Command Prompt / Terminal, lalu instal semua pustaka yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
3. Buka file `config.py` dan masukkan kredensial Anda:
   - Nomor Akun MT5 & Password
   - Nama Server Broker
   - Token Bot Telegram & Chat ID (opsional untuk rapor)

## Cara Menjalankan Bot
### 1. Pelatihan AI (Wajib Pertama Kali)
Sebelum bot bisa digunakan, ia harus belajar dari data historis terbaru untuk membangun struktur logika otaknya. Jalankan:
```bash
python train.py
```
*(Proses ini akan mengunduh data dari MT5 dan melakukan Auto-Tuning yang memakan waktu 1-3 menit. Setelah selesai, file `model_XAUUSDm.pkl` akan tercipta).*

### 2. Live Trading
Setelah AI selesai dilatih, nyalakan bot utama agar ia bisa mengawasi pasar 24 jam nonstop:
```bash
python bot_main.py
```
*(Bot akan mengecek pasar setiap pergantian candle 5 Menit, mengeksekusi order jika menemukan pola probabilitas tinggi, dan mencetak laporan ke Telegram setiap malam).*

### 3. Simulasi Backtest
Jika Anda ingin melihat seberapa akurat strategi AI ini pada data 1 bulan ke belakang, jalankan:
```bash
python backtester.py
```
