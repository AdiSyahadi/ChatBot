import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument

load_dotenv()

# Ambil API key Gemini dari secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Konfigurasi Gemini
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

def ask_gemini_with_data(prompt, df):
    if not gemini_api_key:
        return "❌ GEMINI_API_KEY belum diset"
    try:
        df_sample = df.head(10).to_csv(index=False)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(f"""
Berikut 10 baris pertama data customer:

{df_sample}

Sekarang jawab pertanyaan ini:
{prompt}
""")
        return response.text
    except InvalidArgument:
        return "❌ API key Gemini tidak valid atau model tidak tersedia."
    except Exception as e:
        return f"❌ Gemini Error: {e}"

def show_chatbot(df_customer):
    st.title("🤖 ChatBot Analisis Customer")

    # Hanya ada Gemini sekarang
    model_choice = "Gemini (Google)"
    st.markdown("Model AI: **Gemini (Google)**")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    if prompt := st.chat_input("Tanya tentang data customer..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append(("user", prompt))

        with st.chat_message("assistant"):
            with st.spinner("Sedang menganalisis..."):
                reply = ask_gemini_with_data(prompt, df_customer)
                st.markdown(reply)
                st.session_state.chat_history.append(("assistant", reply))
