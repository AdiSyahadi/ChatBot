import streamlit as st
import gspread
from google.auth.exceptions import DefaultCredentialsError
from oauth2client.service_account import ServiceAccountCredentials
import json

# Ambil service account dari secrets
try:
    service_account_info = st.secrets["google_service_account"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"],
    )
    client = gspread.authorize(credentials)
except KeyError:
    st.error("❌ Gagal menemukan kredensial service account di secrets.")
    st.stop()
except DefaultCredentialsError as e:
    st.error(f"❌ Gagal otentikasi: {e}")
    st.stop()

# Coba buka Spreadsheet
try:
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    spreadsheet = client.open_by_key(sheet_id)
    sheet = spreadsheet.sheet1  # atau nama lain jika pakai sheet lain
    st.success("✅ Berhasil terhubung ke Google Sheet!")
except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ Spreadsheet tidak ditemukan. Periksa ID Spreadsheet kamu.")
    st.stop()
except gspread.exceptions.APIError as e:
    st.error(f"❌ Gagal akses API Google Sheets: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error tak terduga: {e}")
    st.stop()
