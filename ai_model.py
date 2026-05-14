from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_and_save_model(df, model_path="model_rf.pkl"):
    """
    Melatih model Random Forest menggunakan GridSearchCV untuk mencari
    konfigurasi (hyperparameter) terbaik agar tidak bias.
    """
    print("Mempersiapkan data untuk training AI...")
    
    # Fitur-fitur yang akan dipelajari AI dari data_processor.py
    feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                    'body_size', 'upper_shadow', 'lower_shadow', 'ATR']
    
    X = df[feature_cols]
    y = df['target']
    
    # Memisahkan data: 80% untuk training, 20% untuk pengujian (testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    print("\n[AUTO-TUNING] AI sedang mensimulasikan berbagai variasi logika otak...")
    print("Proses ini memakan banyak CPU dan waktu (1-3 menit). Harap tunggu...")
    
    # Menyiapkan ruang pencarian logika (Grid)
    # AI akan mencoba kombinasi dari angka-angka di bawah ini
    param_grid = {
        'n_estimators': [50, 100, 200],      # Berapa banyak "pohon" keputusan
        'max_depth': [3, 5, 10, None],       # Seberapa dalam/detail AI berpikir
        'min_samples_split': [2, 5, 10]      # Saringan kepekaan (anti-noise)
    }
    
    # TimeSeriesSplit mencegah AI "mengintip masa depan" saat proses ujian mandiri
    tscv = TimeSeriesSplit(n_splits=3)
    
    # Inisialisasi mesin pencari Grid
    rf_base = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(estimator=rf_base, param_grid=param_grid, 
                               cv=tscv, scoring='accuracy', n_jobs=-1, verbose=0)
                               
    # Mulai mengeksplorasi ratusan kombinasi
    grid_search.fit(X_train, y_train)
    
    # Ambil logika pemenang
    best_model = grid_search.best_estimator_
    print("\n[SUKSES] AI berhasil menemukan kombinasi logika terbaik untuk saat ini!")
    print(f"Logika yang dipilih: {grid_search.best_params_}")
    
    # Mengevaluasi model terbaik tersebut pada data uji
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAkurasi Logika Baru pada Data Uji: {acc * 100:.2f}%")
    print("Laporan Detail:")
    print(classification_report(y_test, y_pred))
    
    # Menyimpan otak AI ke file
    joblib.dump(best_model, model_path)
    print(f"Otak AI mutakhir berhasil disimpan di: {model_path}")
    
    return best_model

def load_model(model_path="model_rf.pkl"):
    """Memuat model AI yang sudah dilatih sebelumnya dari file."""
    if not os.path.exists(model_path):
        print(f"File model {model_path} tidak ditemukan. Harus ditraining dulu.")
        return None
    return joblib.load(model_path)
