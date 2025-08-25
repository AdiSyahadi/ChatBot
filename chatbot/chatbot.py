import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import DefaultCredentialsError

# Import modul-modul halaman
from home import home
from data_customer import data_customer
from chatbot import chatbot

# ========== STYLING ========== #
st.markdown("""
<style>
    /* (Salin style CSS-mu di sini) */
</style>
""", unsafe_allow_html=True)

# ========== AMBIL VARIABEL DARI SECRETS ========== #
sheet2_url = st.secrets["GOOGLE_SHEET_URL"]
SERVICE_ACCOUNT = st.secrets["google_service_account"]
SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
openai_api_key = st.secrets["OPENAI_API_KEY"]
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# ========== FUNGSI ========== #

def load_data_from_google_sheet():
    """Memuat data customer dari Google Sheets"""
    try:
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
    except DefaultCredentialsError as e:
        st.error("❌ Gagal membuat kredensial dari service account.")
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error("❌ Error saat memuat kredensial:")
        st.error(str(e))
        st.stop()

    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID)
        worksheet = sheet.sheet1  # atau worksheet("Sheet1")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Spreadsheet tidak ditemukan. Periksa kembali GOOGLE_SHEET_ID.")
        st.stop()
    except gspread.exceptions.APIError as e:
        st.error("❌ Gagal mengakses Google Sheets API.")
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error("❌ Error tidak terduga saat memuat Google Sheets:")
        st.error(str(e))
        st.stop()

# ========== LOAD DATA ========== #
try:
    # Mengambil data dari Google Sheet
    df_customer = load_data_from_google_sheet()
    if df_customer.empty:
        st.error("❌ Data customer kosong.")
        st.stop()
except Exception as e:
    st.error("❌ Gagal memuat data dari Google Sheets.")
    st.error(str(e))
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
    # Memanggil fungsi chatbot dari chatbot.py
    chatbot.show_chatbot(df_customer, openai_api_key, gemini_api_key)
