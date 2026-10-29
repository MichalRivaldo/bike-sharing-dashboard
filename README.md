# Proyek Analisis Data: Bike Sharing Dataset 🚲

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C.) tahun 2011-2012, lengkap dengan dashboard interaktif menggunakan Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa puncak penyewaan terjadi pada hari kerja vs akhir pekan/libur, dan berapa selisihnya?
2. Bagaimana pengaruh musim dan cuaca terhadap rata-rata penyewaan harian, dan berapa pertumbuhan 2012 vs 2011?

## Struktur Direktori
```
submission
├───dashboard
|   ├───main_data.csv   (data per jam yang sudah dibersihkan)
|   ├───day_data.csv    (data harian yang sudah dibersihkan)
|   └───dashboard.py
├───data
|   ├───day.csv
|   └───hour.csv
├───notebook.ipynb
├───README.md
└───requirements.txt
```

## Setup Environment
Disarankan memakai Python 3.10 atau lebih baru.

```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Menjalankan Dashboard
Jalankan perintah berikut dari folder `submission`:

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`.

## Menjalankan Notebook
Buka `notebook.ipynb` dari folder `submission` (agar jalur `data/` dan `dashboard/` terbaca), lalu jalankan semua sel (`Run All`).

## Sumber Data
Fanaee-T, Hadi, and Gama, Joao. "Event labeling combining ensemble detectors and background knowledge." Progress in Artificial Intelligence (2013): 1-15.
