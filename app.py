import streamlit as st
import pandas as pd
import os
import qrcode
from PIL import Image, ImageDraw
import base64
from io import BytesIO

st.set_page_config(page_title="Pendaftaran 17 Agustus", layout="centered")

DATA_FILE = "data_peserta.csv"
FOTO_FOLDER = "foto_peserta"
KARTU_FOLDER = "kartu_peserta"

os.makedirs(FOTO_FOLDER, exist_ok=True)
os.makedirs(KARTU_FOLDER, exist_ok=True)

# Background gradasi merah ke putih
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #ff0000, #ffffff);
        background-attachment: fixed;
    }
    </style>
""", unsafe_allow_html=True)

# Fungsi login admin
def login_admin(username, password):
    return username == "admin" and password == "admin123"

# Fungsi kategori umur
def tentukan_kategori(umur):
    if umur <= 12:
        return "Anak-anak"
    elif umur <= 17:
        return "Remaja"
    else:
        return "Dewasa"

# Fungsi simpan data
def simpan_data(data_baru):
    if os.path.exists(DATA_FILE):
        df_lama = pd.read_csv(DATA_FILE)
        df_baru = pd.DataFrame([data_baru])
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = pd.DataFrame([data_baru])
    df.to_csv(DATA_FILE, index=False)

# Fungsi buat kartu peserta
def buat_kartu_peserta(data):
    qr = qrcode.make(f"{data['Nama']} - {data['Lomba']} - {data['Kategori Umur']}")
    qr = qr.resize((100, 100))
    kartu = Image.new("RGB", (400, 200), color=(255, 255, 255))
    
    foto_path = os.path.join(FOTO_FOLDER, data['Foto'])
    if os.path.exists(foto_path):
        foto = Image.open(foto_path).resize((100, 120))
        kartu.paste(foto, (20, 40))
    kartu.paste(qr, (280, 50))

    draw = ImageDraw.Draw(kartu)
    draw.text((140, 40), f"Nama: {data['Nama']}", fill="black")
    draw.text((140, 70), f"Lomba: {data['Lomba']}", fill="black")
    draw.text((140, 100), f"Kategori: {data['Kategori Umur']}", fill="black")

    kartu_path = os.path.join(KARTU_FOLDER, f"{data['Nama']}.png")
    kartu.save(kartu_path)
    return kartu_path

# Header logo + judul tengah
with st.container():
    col1, col2 = st.columns([1, 6])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)
        else:
            st.warning("Logo tidak ditemukan.")
    with col2:
        st.markdown(
            "<h1 style='text-align: center; color: black;'>PENDAFTARAN 17 AGUSTUS 2025<br>RT.06/02 PINANG 4</h1>",
            unsafe_allow_html=True
        )

# Menu
menu = st.sidebar.selectbox("Menu", ["🏠 Daftar Peserta", "🔐 Login Admin"])

if menu == "🏠 Daftar Peserta":
    nama = st.text_input("Nama Lengkap")
    umur = st.number_input("Umur", 1, 100, step=1)
    tanggal_lahir = st.text_input("Tanggal Lahir (YYYY-MM-DD)")
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    kategori = tentukan_kategori(umur)

    if kategori == "Anak-anak":
        lomba = st.selectbox("Pilih Lomba", ["Balap Karung", "Makan Kerupuk"])
    elif kategori == "Remaja":
        lomba = st.selectbox("Pilih Lomba", ["Tarik Tambang", "Panjat Pinang"])
    else:
        lomba = st.selectbox("Pilih Lomba", ["Lomba Masak", "Tenis Meja"])

    foto = st.file_uploader("Upload Foto", type=["jpg", "jpeg", "png"])

    if st.button("Daftar"):
        if nama and tanggal_lahir and foto:
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                if nama in df["Nama"].values:
                    st.warning("Kamu sudah pernah mendaftar.")
                    st.stop()

            foto_nama = f"{nama.replace(' ', '_')}.jpg"
            foto_path = os.path.join(FOTO_FOLDER, foto_nama)
            with open(foto_path, "wb") as f:
                f.write(foto.getbuffer())

            data = {
                "Nama": nama,
                "Umur": umur,
                "Tanggal Lahir": tanggal_lahir,
                "Jenis Kelamin": jenis_kelamin,
                "Kategori Umur": kategori,
                "Lomba": lomba,
                "Foto": foto_nama
            }
            simpan_data(data)
            st.success("Pendaftaran berhasil!")

            kartu_path = buat_kartu_peserta(data)
            st.image(kartu_path, width=350)
            with open(kartu_path, "rb") as f:
                st.download_button("⬇️ Download Kartu", f, file_name=f"{nama}.png", mime="image/png")
        else:
            st.warning("Isi semua data dan unggah foto terlebih dahulu.")

elif menu == "🔐 Login Admin":
    st.subheader("Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_admin(username, password):
            st.success("Login berhasil!")
            st.subheader("📋 Data Peserta")

            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                st.dataframe(df)
                st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="data_peserta.csv", mime="text/csv")
            else:
                st.info("Belum ada peserta terdaftar.")
        else:
            st.error("Login gagal.")
