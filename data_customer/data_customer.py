import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def get_gsheet_client():
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

def load_data():
    client = get_gsheet_client()
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).worksheet("Sheet1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df, sheet

def show(df_customer):
    st.title("📗 Data Customer (CRUD)")
    df, sheet = load_data()

    st.subheader("📋 Tabel Data Customer")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("➕ Tambah Data Customer")

    with st.form("form_tambah"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama")
            nama_perusahaan = st.text_input("Nama Perusahaan")
            email = st.text_input("Email")
            whatsapp = st.text_input("WhatsApp")
            website = st.text_input("Website")
            instagram = st.text_input("Instagram")
        with col2:
            tanggal_meeting = st.date_input("Tanggal Meeting")
            kebutuhan_layanan = st.text_input("Kebutuhan Layanan")
            sumber = st.text_input("Sumber")
            link_kalender = st.text_input("Link Kalender")

        submitted = st.form_submit_button("Simpan")

        if submitted:
            tanggal_submit = datetime.today().strftime("%Y-%m-%d")
            new_row = [tanggal_submit, str(tanggal_meeting), nama, nama_perusahaan, email, whatsapp, website, instagram, kebutuhan_layanan, sumber, link_kalender]
            sheet.append_row(new_row)
            st.success("✅ Data berhasil ditambahkan.")
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("✏️ Edit Data Customer")

    edit_index = st.number_input("Masukkan nomor baris yang ingin diedit (mulai dari 2)", min_value=2, step=1)
    if edit_index <= len(df) + 1:
        row_data = sheet.row_values(edit_index)
        if len(row_data) < 11:
            row_data += [""] * (11 - len(row_data))

        with st.form("form_edit"):
            col1, col2 = st.columns(2)
            with col1:
                nama = st.text_input("Nama", value=row_data[2])
                nama_perusahaan = st.text_input("Nama Perusahaan", value=row_data[3])
                email = st.text_input("Email", value=row_data[4])
                whatsapp = st.text_input("WhatsApp", value=row_data[5])
                website = st.text_input("Website", value=row_data[6])
                instagram = st.text_input("Instagram", value=row_data[7])
            with col2:
                tanggal_meeting = st.text_input("Tanggal Meeting", value=row_data[1])
                kebutuhan_layanan = st.text_input("Kebutuhan Layanan", value=row_data[8])
                sumber = st.text_input("Sumber", value=row_data[9])
                link_kalender = st.text_input("Link Kalender", value=row_data[10])

            update_submit = st.form_submit_button("Update Data")

            if update_submit:
                tanggal_submit = row_data[0]  # tidak diubah
                updated_row = [tanggal_submit, tanggal_meeting, nama, nama_perusahaan, email, whatsapp, website, instagram, kebutuhan_layanan, sumber, link_kalender]
                sheet.update(f"A{edit_index}:K{edit_index}", [updated_row])
                st.success(f"✅ Baris ke-{edit_index} berhasil diperbarui.")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("🗑️ Hapus Data Customer")

    index_to_delete = st.number_input("Masukkan nomor baris yang ingin dihapus (mulai dari 2)", min_value=2, step=1, key="delete")
    if st.button("Hapus Baris"):
        sheet.delete_rows(index_to_delete)
        st.success(f"✅ Baris ke-{index_to_delete} berhasil dihapus.")
        st.experimental_rerun()
