from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

BASE_DIR = Path(__file__).parent
WARNA_TIPE = {"Hari Kerja": "#1f5f99", "Akhir Pekan/Libur": "#e07b39"}
URUTAN_MUSIM = ["Spring", "Summer", "Fall", "Winter"]
URUTAN_CUACA = ["Cerah/Sedikit Berawan", "Berkabut/Berawan", "Hujan/Salju Ringan"]


@st.cache_data
def load_data():
    day = pd.read_csv(BASE_DIR / "day_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    return day, hour


def segmen_waktu(jam):
    if jam <= 5:
        return "Dini Hari (00-05)"
    if jam <= 9:
        return "Pagi (06-09)"
    if jam <= 15:
        return "Siang (10-15)"
    if jam <= 19:
        return "Sore (16-19)"
    return "Malam (20-23)"


day_df, hour_df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("🚲 Filter")
min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)
musim_pilihan = st.sidebar.multiselect("Musim", URUTAN_MUSIM, default=URUTAN_MUSIM)
st.sidebar.caption("Sumber data: Capital Bikeshare (Washington D.C.), 2011-2012.")

if isinstance(rentang, tuple) and len(rentang) == 2:
    start, end = pd.Timestamp(rentang[0]), pd.Timestamp(rentang[1])
else:
    start, end = pd.Timestamp(min_date), pd.Timestamp(max_date)

day_f = day_df[day_df["dteday"].between(start, end) & day_df["season"].isin(musim_pilihan)]
hour_f = hour_df[hour_df["dteday"].between(start, end) & hour_df["season"].isin(musim_pilihan)]

# ---------------- Header & KPI ----------------
st.title("Dashboard Analisis Bike Sharing")
st.caption("Pola penyewaan sepeda menurut jam, musim, cuaca, dan suhu.")

if day_f.empty or hour_f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah rentang tanggal atau musim.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total penyewaan", f"{day_f['cnt'].sum():,.0f}")
k2.metric("Rata-rata per hari", f"{day_f['cnt'].mean():,.0f}")
k3.metric("Porsi pengguna registered", f"{day_f['registered'].sum() / day_f['cnt'].sum():.0%}")
k4.metric("Jumlah hari", f"{len(day_f)}")

tab1, tab2, tab3 = st.tabs(["⏰ Pola per Jam", "🌦️ Musim & Cuaca", "🧩 Segmentasi"])

# ---------------- Tab 1: Pertanyaan 1 ----------------
with tab1:
    st.subheader("Pertanyaan 1: Pada jam berapa rata-rata penyewaan sepeda per jam mencapai puncak pada hari kerja dibandingkan akhir pekan/hari libur, dan berapa selisih rata-ratanya pada jam puncak tersebut?")
    st.caption("Periode analisis: 2011-2012 (dapat difilter di sidebar).")
    hourly = hour_f.groupby(["day_type", "hour"])["cnt"].mean().unstack(0)

    fig, ax = plt.subplots(figsize=(11, 5))
    for tipe in hourly.columns:
        ax.plot(hourly.index, hourly[tipe], marker="o", markersize=4, linewidth=2.5,
                color=WARNA_TIPE[tipe], label=tipe)
        jam_puncak, nilai_puncak = hourly[tipe].idxmax(), hourly[tipe].max()
        ax.annotate(f"Puncak {int(jam_puncak):02d}.00\n{nilai_puncak:,.0f} sewa/jam",
                    xy=(jam_puncak, nilai_puncak), xytext=(jam_puncak + 0.6, nilai_puncak * 1.08),
                    color=WARNA_TIPE[tipe], fontweight="bold")
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata penyewaan per jam (sepeda)")
    ax.set_xticks(range(0, 24, 2))
    ax.set_ylim(0, hourly.max().max() * 1.3)
    ax.legend(frameon=False, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    kerja = hour_f[hour_f["day_type"] == "Hari Kerja"]
    libur = hour_f[hour_f["day_type"] == "Akhir Pekan/Libur"]
    c1, c2 = st.columns(2)
    if not kerja.empty:
        porsi = kerja[kerja["hour"].isin([7, 8, 9, 16, 17, 18, 19])]["cnt"].sum() / kerja["cnt"].sum()
        c1.info(f"**Hari kerja:** jam 07-09 dan 16-19 menyumbang **{porsi:.0%}** penyewaan.")
    if not libur.empty:
        porsi = libur[libur["hour"].between(11, 16)]["cnt"].sum() / libur["cnt"].sum()
        c2.info(f"**Akhir pekan/libur:** jam 11-16 menyumbang **{porsi:.0%}** penyewaan.")

# ---------------- Tab 2: Pertanyaan 2 ----------------
with tab2:
    st.subheader("Pertanyaan 2: Musim dan kondisi cuaca apa yang memiliki rata-rata penyewaan sepeda harian tertinggi dan terendah, serta berapa persen pertumbuhan rata-rata penyewaan harian 2012 dibandingkan 2011?")
    st.caption("Periode analisis: 2011-2012 (dapat difilter di sidebar).")
    col_a, col_b = st.columns([1.3, 1])

    with col_a:
        fig, ax = plt.subplots(figsize=(7, 5))
        musim_ada = [m for m in URUTAN_MUSIM if m in day_f["season"].unique()]
        sns.barplot(data=day_f, x="season", y="cnt", hue="year", order=musim_ada,
                    errorbar=None, palette={2011: "#a9c4de", 2012: "#1f5f99"}, ax=ax)
        for wadah in ax.containers:
            ax.bar_label(wadah, fmt="%.0f", padding=2, fontsize=9)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_title("Rata-rata penyewaan harian per musim dan tahun", loc="left", fontweight="bold", fontsize=11)
        if ax.get_legend():
            ax.legend(title="Tahun", frameon=False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        cuaca = day_f.groupby("weather")["cnt"].agg(["mean", "count"]).reindex(URUTAN_CUACA).dropna()
        fig, ax = plt.subplots(figsize=(5.5, 5))
        warna = ["#1f5f99", "#9db7cf", "#c9d6e3"][: len(cuaca)]
        batang = ax.bar([n.replace("/", "/\n") for n in cuaca.index], cuaca["mean"], color=warna)
        for b, (nilai, n) in zip(batang, zip(cuaca["mean"], cuaca["count"])):
            ax.text(b.get_x() + b.get_width() / 2, nilai + cuaca["mean"].max() * 0.02,
                    f"{nilai:,.0f}\n({int(n)} hari)", ha="center", fontsize=9)
        ax.set_xlabel("Kondisi cuaca")
        ax.set_ylabel("Rata-rata penyewaan harian (sepeda)")
        ax.set_ylim(0, cuaca["mean"].max() * 1.25)
        ax.set_title("Rata-rata penyewaan harian per cuaca", loc="left", fontweight="bold", fontsize=11)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    rata_tahun = day_f.groupby("year")["cnt"].mean()
    if {2011, 2012}.issubset(rata_tahun.index):
        st.success(f"Pertumbuhan rata-rata penyewaan harian 2012 vs 2011: "
                   f"**{rata_tahun[2012] / rata_tahun[2011] - 1:+.0%}** "
                   f"({rata_tahun[2011]:,.0f} → {rata_tahun[2012]:,.0f}).")
    else:
        st.caption("Pilih rentang tanggal yang mencakup 2011 dan 2012 untuk melihat pertumbuhan tahunan.")

# ---------------- Tab 3: Analisis lanjutan ----------------
with tab3:
    st.subheader("Manual grouping & binning")
    col_c, col_d = st.columns(2)

    with col_c:
        h = hour_f.copy()
        h["time_segment"] = h["hour"].apply(segmen_waktu)
        urutan_seg = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"]
        seg = h.groupby(["time_segment", "day_type"])["cnt"].mean().unstack().reindex(urutan_seg)
        fig, ax = plt.subplots(figsize=(7, 5))
        seg.plot(kind="bar", ax=ax, color=[WARNA_TIPE[c] for c in seg.columns], width=0.75)
        for wadah in ax.containers:
            ax.bar_label(wadah, fmt="%.0f", padding=2, fontsize=8)
        ax.set_xlabel("")
        ax.set_ylabel("Rata-rata penyewaan per jam")
        ax.set_title("Rata-rata sewa per jam menurut segmen waktu", loc="left", fontweight="bold", fontsize=11)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
        ax.legend(frameon=False, title="")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_d:
        d = day_f.copy()
        d["temp_group"] = pd.cut(d["temp_c"], bins=[-np.inf, 10, 20, 30, np.inf],
                                 labels=["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"])
        suhu = d.groupby("temp_group", observed=True)["cnt"].agg(["mean", "count"])
        fig, ax = plt.subplots(figsize=(6, 5))
        batang = ax.bar(suhu.index.astype(str), suhu["mean"], color="#1f5f99")
        for b, (nilai, n) in zip(batang, zip(suhu["mean"], suhu["count"])):
            ax.text(b.get_x() + b.get_width() / 2, nilai + suhu["mean"].max() * 0.02,
                    f"{nilai:,.0f}\n({int(n)} hari)", ha="center", fontsize=9)
        ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_ylim(0, suhu["mean"].max() * 1.25)
        ax.set_title("Rata-rata penyewaan harian per kelompok suhu", loc="left", fontweight="bold", fontsize=11)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

st.divider()
st.subheader("Rekomendasi")
st.markdown(
    "- **Redistribusi sepeda** mengikuti jam komuter hari kerja (sebelum 07.00 dan 16.00); gunakan dini hari sebagai jendela perawatan.\n"
    "- **Akhir pekan:** perkuat stok di area rekreasi pada jam 11.00-16.00 dan fokuskan promo untuk pengguna *casual*.\n"
    "- **Musiman:** jadwalkan perawatan besar saat Spring, siapkan kapasitas penuh pada Summer-Fall.\n"
    "- **Cuaca buruk:** sesuaikan operasional karena permintaan turun hingga sekitar 63% pada hari hujan/salju ringan."
)
st.caption("Data: Fanaee-T & Gama (2013), Capital Bikeshare 2011-2012.")
