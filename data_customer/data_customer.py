import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def get_gsheet_client():
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client

def load_data():
    client = get_gsheet_client()
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).worksheet("Sheet1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df, sheet

def show(df_customer):
    st.title("📗 Data Customer")

    df, sheet = load_data()

    # ⬅️ Sidebar untuk aksi CRUD
    st.sidebar.title("🛠️ Aksi Data Customer")
    action = st.sidebar.radio("Pilih Aksi", ["Tambah", "Edit", "Hapus"])

    if action == "Tambah":
        st.sidebar.subheader("➕ Tambah Customer")
        with st.sidebar.form("form_tambah"):
            nama = st.text_input("Nama")
            nama_perusahaan = st.text_input("Nama Perusahaan")
            email = st.text_input("Email")
            whatsapp = st.text_input("WhatsApp")
            website = st.text_input("Website")
            instagram = st.text_input("Instagram")
            tanggal_meeting = st.date_input("Tanggal Meeting")
            kebutuhan_layanan = st.text_input("Kebutuhan Layanan")
            sumber = st.text_input("Sumber")
            link_kalender = st.text_input("Link Kalender")

            submitted = st.form_submit_button("Simpan")
            if submitted:
                tanggal_submit = datetime.today().strftime("%Y-%m-%d")
                new_row = [
                    tanggal_submit, str(tanggal_meeting), nama, nama_perusahaan, email,
                    whatsapp, website, instagram, kebutuhan_layanan, sumber, link_kalender
                ]
                sheet.append_row(new_row)
                st.success("✅ Data berhasil ditambahkan.")
                st.rerun()

    elif action == "Edit":
        st.sidebar.subheader("✏️ Edit Customer")
        edit_index = st.sidebar.number_input(
            "Nomor Baris (mulai dari 2)", min_value=2, step=1
        )
        if edit_index <= len(df) + 1:
            row_data = sheet.row_values(edit_index)
            if len(row_data) < 11:
                row_data += [""] * (11 - len(row_data))

            with st.sidebar.form("form_edit"):
                nama = st.text_input("Nama", value=row_data[2])
                nama_perusahaan = st.text_input("Nama Perusahaan", value=row_data[3])
                email = st.text_input("Email", value=row_data[4])
                whatsapp = st.text_input("WhatsApp", value=row_data[5])
                website = st.text_input("Website", value=row_data[6])
                instagram = st.text_input("Instagram", value=row_data[7])
                tanggal_meeting = st.text_input("Tanggal Meeting", value=row_data[1])
                kebutuhan_layanan = st.text_input("Kebutuhan Layanan", value=row_data[8])
                sumber = st.text_input("Sumber", value=row_data[9])
                link_kalender = st.text_input("Link Kalender", value=row_data[10])

                update_submit = st.form_submit_button("Update Data")
                if update_submit:
                    tanggal_submit = row_data[0]
                    updated_row = [
                        tanggal_submit, tanggal_meeting, nama, nama_perusahaan, email,
                        whatsapp, website, instagram, kebutuhan_layanan, sumber, link_kalender
                    ]
                    sheet.update(f"A{edit_index}:K{edit_index}", [updated_row])
                    st.success(f"✅ Baris ke-{edit_index} berhasil diperbarui.")
                    st.rerun()

    elif action == "Hapus":
        st.sidebar.subheader("🗑️ Hapus Customer")
        index_to_delete = st.sidebar.number_input(
            "Nomor Baris (mulai dari 2)", min_value=2, step=1, key="delete"
        )
        if st.sidebar.button("Hapus Baris"):
            sheet.delete_rows(index_to_delete)
            st.success(f"✅ Baris ke-{index_to_delete} berhasil dihapus.")
            st.rerun()

    # 📋 Tabel tetap di halaman utama
    st.subheader("📋 Tabel Data Customer")
    st.dataframe(df, use_container_width=True)
