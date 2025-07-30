import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ========== AUTHENTIKASI GOOGLE SHEET ========== #
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(credentials)

# Ganti sesuai nama file & sheet
SHEET_NAME = "Data Meson"
SHEET_TAB = "Sheet1"

sheet = client.open(SHEET_NAME).worksheet(SHEET_TAB)

# ========== LOAD DATA ========== #
def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# ========== SIMPAN DATA (TAMBAH) ========== #
def append_data(data: dict):
    sheet.append_row(list(data.values()))

# ========== UPDATE DATA (berdasar baris) ========== #
def update_data(row_index: int, data: dict):
    for i, val in enumerate(data.values(), start=1):
        sheet.update_cell(row_index + 2, i, val)  # +2 karena header + index mulai dari 1

# ========== DELETE DATA ========== #
def delete_row(row_index: int):
    sheet.delete_rows(row_index + 2)  # +2 karena header + index mulai dari 1

# ========== TAMPILKAN UI CRUD ========== #
def show(df_customer):
    st.title("📗 TABEL DATA CUSTOMER (CRUD)")

    # BACA / READ
    df = load_data()
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # TAMBAH / CREATE
    with st.expander("➕ Tambah Data Baru"):
        with st.form("add_form"):
            data_baru = {}
            for col in df.columns:
                data_baru[col] = st.text_input(f"{col}")
            submitted = st.form_submit_button("Simpan")
            if submitted:
                append_data(data_baru)
                st.success("✅ Data berhasil ditambahkan")

    # UPDATE
    st.markdown("### ✏️ Edit Data")
    selected_index = st.number_input("Pilih nomor baris yang akan diubah (mulai dari 0)", min_value=0, max_value=len(df)-1, step=1)
    row_data = df.iloc[selected_index]

    with st.form("update_form"):
        updated_data = {}
        for col in df.columns:
            updated_data[col] = st.text_input(f"{col}", value=row_data[col])
        update_btn = st.form_submit_button("Update")
        if update_btn:
            update_data(selected_index, updated_data)
            st.success("✅ Data berhasil diupdate")

    # DELETE
    st.markdown("### 🗑️ Hapus Data")
    delete_index = st.number_input("Pilih nomor baris yang akan dihapus (mulai dari 0)", min_value=0, max_value=len(df)-1, key="delete_index")
    if st.button("Hapus Data"):
        delete_row(delete_index)
        st.success("✅ Data berhasil dihapus")
