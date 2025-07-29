# main.py
import streamlit as st
import pandas as pd

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

# ========== LOAD GOOGLE SHEET ========== #
sheet2_url = st.secrets["GOOGLE_SHEET_URL"]

@st.cache_data
def load_data(sheet_url):
    return pd.read_csv(sheet_url)

try:
    df_customer_raw = load_data(sheet2_url)
    # Hapus kolom Unnamed jika ada (biasanya dari index)
    df_customer = df_customer_raw.loc[:, ~df_customer_raw.columns.str.contains("^Unnamed")]
except Exception as e:
    st.error("❌ Gagal memuat data Google Sheets")
    st.stop()

# ========== SIDEBAR ========== #
with st.sidebar:
    st.title("📊 Navigasi")
    menu = st.radio("Pilih halaman:", ["🏠 Home", "📗 Data Customer", "🤖 ChatBot"])

# ========== ROUTING ========== #
if menu == "🏠 Home":
    home.home.show()
elif menu == "📗 Data Customer":
    data_customer.data_customer.show(df_customer)
elif menu == "🤖 ChatBot":
    chatbot.chatbot.show_chatbot(df_customer)
