# main.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Import modul-modul halaman
from home import home
from data_customer import data_customer
from chatbot import chatbot

# ========== CONFIGURASI ========== #
st.set_page_config(page_title="System Meslon Digital", layout="wide")

# ========== STYLE TAMBAHAN ========== #
st.markdown("""<style>
    /* (Salin style CSS-mu di sini) */
</style>""", unsafe_allow_html=True)

# ========== AUTENTIKASI & KONEKSI GOOGLE SHEET ========== #
SERVICE_ACCOUNT = st.secrets["google_service_account"]
SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]

@st.cache_data
def load_data_from_google_sheet():
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.sheet1  # atau gunakan .worksheet("Nama Sheet")
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

try:
    df_customer = load_data_from_google_sheet()
except Exception as e:
    st.error("❌ Gagal memuat data dari Google Sheets. Pastikan akses dan ID sudah benar.")
    st.stop()

# ========== SIDEBAR ========== #
with st.sidebar:
    st.title("📊 Navigasi")
    menu = st.radio("Pilih halaman:", ["🏠 Home", "📗 Data Customer", "🤖 ChatBot"])

# ========== ROUTING ========== #
if menu == "🏠 Home":
    home.show()
elif menu == "📗 Data Customer":
    data_customer.show(df_customer)
elif menu == "🤖 ChatBot":
    chatbot.show_chatbot(df_customer)
