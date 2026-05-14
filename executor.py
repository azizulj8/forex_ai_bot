import MetaTrader5 as mt5
import config

def calculate_lot_size(symbol, stop_loss_pips):
    """
    Menghitung ukuran lot berdasarkan persentase risiko dari saldo (config.RISK_PERCENT).
    Menerapkan Money Management otomatis agar kerugian tidak melebihi batas.
    """
    account_info = mt5.account_info()
    if account_info is None:
        print("Gagal mendapatkan info akun MT5")
        return 0.01 # Default lot terkecil jika gagal

    balance = account_info.balance
    risk_amount = balance * config.RISK_PERCENT
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.01
        
    # Pendekatan konversi pip value (1 pip standard = $10)
    # Ini sangat bergantung pada jenis mata uang, tetapi kita buat perkiraan aman
    tick_value = symbol_info.trade_tick_value
    
    # Konversi pips menjadi points/ticks
    sl_ticks = stop_loss_pips * 10 
    
    if tick_value > 0 and sl_ticks > 0:
        lot_size = risk_amount / (sl_ticks * tick_value)
    else:
        lot_size = 0.01

    # Pembatasan lot agar sesuai aturan broker (minimal dan maksimal lot)
    if lot_size < symbol_info.volume_min:
        lot_size = symbol_info.volume_min
    elif lot_size > symbol_info.volume_max:
        lot_size = symbol_info.volume_max
        
    # Membulatkan lot sesuai spesifikasi instrumen (contoh: kelipatan 0.01)
    lot_step = symbol_info.volume_step
    lot_size = round(lot_size / lot_step) * lot_step

    return lot_size

def send_order(symbol, order_type, lot_size, sl_price, tp_price):
    """
    Fungsi teknis untuk mengirim data transaksi ke server Exness/MT5.
    """
    symbol_info = mt5.symbol_info(symbol)
    
    # Dapatkan harga sekarang
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": price,
        "sl": float(sl_price),
        "tp": float(tp_price),
        "deviation": 20, # Slippage maksimal 20 points
        "magic": 999111, # ID Unik agar tidak bentrok dengan transaksi manual Anda
        "comment": "AI Bot - Risk 1:2",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Kirim order
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Gagal mengirim order. Error Code: {result.retcode}")
        return None
        
    print(f"ORDER BERHASIL! Tiket No: {result.order}")
    return result

def execute_trade_signal(symbol, signal_is_buy, sl_pips=20):
    """
    Fungsi yang akan dipanggil oleh AI saat ada sinyal trading baru.
    Akan otomatis menghitung SL dan TP rasio 1:2.
    """
    lot_size = calculate_lot_size(symbol, sl_pips)
    print(f"Mengkalkulasi Lot: {lot_size} lot untuk menjaga risiko {config.RISK_PERCENT * 100}%")
    
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point
    digits = symbol_info.digits
    
    tick = mt5.symbol_info_tick(symbol)
    
    # 1. Dapatkan informasi spread dan batas minimum broker
    min_stop_points = symbol_info.trade_stops_level
    spread_price = tick.ask - tick.bid
    
    # 2. Konversi pips permintaan user ke jarak harga aktual
    # Konversi otomatis untuk Gold (XAU), JPY, atau Forex Standar
    if "XAU" in symbol or "GOLD" in symbol:
        pip_multiplier = 0.1 / point
    elif "JPY" in symbol:
        pip_multiplier = 0.01 / point
    else:
        pip_multiplier = 0.0001 / point
        
    sl_points = sl_pips * pip_multiplier
    sl_price_distance = sl_points * point 
    
    # 3. Validasi Keamanan MT5 (Penyebab utama Error 10016)
    # Jarak SL HARUS lebih besar dari Spread + Stops_Level agar tidak bentrok dengan harga berlawanan.
    safe_min_distance = spread_price + (min_stop_points * point) + (2 * point)
    
    if sl_price_distance <= safe_min_distance:
        sl_price_distance = safe_min_distance + (5 * point)
        print(f"Perhatian: SL diperlebar otomatis karena jarak aslinya menabrak Spread broker!")
        
    tp_price_distance = sl_price_distance * config.RISK_REWARD_RATIO

    if signal_is_buy:
        current_price = tick.ask
        sl_price = round(current_price - sl_price_distance, digits)
        tp_price = round(current_price + tp_price_distance, digits)
        print(f"Sinyal BUY Tereksekusi! Harga: {current_price} | SL: {sl_price} | TP: {tp_price}")
        return send_order(symbol, mt5.ORDER_TYPE_BUY, lot_size, sl_price, tp_price)
    else:
        current_price = tick.bid
        sl_price = round(current_price + sl_price_distance, digits)
        tp_price = round(current_price - tp_price_distance, digits)
        print(f"Sinyal SELL Tereksekusi! Harga: {current_price} | SL: {sl_price} | TP: {tp_price}")
        return send_order(symbol, mt5.ORDER_TYPE_SELL, lot_size, sl_price, tp_price)
