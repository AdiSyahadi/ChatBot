import streamlit as st
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # ← LangChain untuk Gemini
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument
import requests  # Untuk kirim ke webhook
import json

# Load API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
webhook_url = os.getenv("AGENT_WEBHOOK_URL")  # URL Webhook ke n8n

openai_client = OpenAI(api_key=openai_api_key)

# Konfigurasi Gemini untuk LangChain
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)


def ask_openai_with_data(prompt, df):
    try:
        df_sample = df.head(10).to_csv(index=False)
        prompt_with_data = f"""
Berikut adalah data customer (10 baris pertama):

{df_sample}

Sekarang jawab pertanyaan ini:
{prompt}
"""
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah analis data customer yang cerdas dan ramah."},
                {"role": "user", "content": prompt_with_data}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ GPT Error: {e}"


def ask_gemini_with_data(prompt, df):
    if not gemini_api_key:
        return "❌ GEMINI_API_KEY belum diset"
    try:
        # Ambil sampel data
        df_sample = df.head(10).to_csv(index=False)

        # Prompt lengkap
        full_prompt = f"""
Berikut 10 baris pertama data customer:

{df_sample}

Jawab pertanyaan ini berdasarkan data:
{prompt}
"""

        # Inisialisasi model LangChain dengan Gemini
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.4,
            google_api_key=gemini_api_key,
            convert_system_message_to_human=True  # Gemini tidak support system message langsung
        )

        # Generate response
        response = llm.invoke(full_prompt)
        return response.content

    except Exception as e:
        return f"❌ Gemini (LangChain) Error: {e}"


def send_to_webhook(prompt):
    """Kirim prompt ke webhook N8N dengan penanganan error aman."""
    if not webhook_url:
        return "❌ Webhook URL belum diset di environment (AGENT_WEBHOOK_URL)"
    try:
        res = requests.post(webhook_url, json={"prompt": prompt})

        if res.status_code == 200:
            # Kalau body kosong
            if not res.text.strip():
                return "✅ Pesan terkirim, tapi tidak ada balasan dari agent."

            # Coba parsing JSON
            try:
                data = res.json()
                return data.get("reply") or data.get("output") or "✅ Pesan terkirim, tapi tidak ada balasan JSON."
            except ValueError:
                # Kalau bukan JSON valid, kirim raw text
                return f"✅ Pesan terkirim. Respons teks: {res.text}"

        else:
            return f"❌ Webhook Error: {res.status_code} - {res.text}"

    except Exception as e:
        return f"❌ Gagal kirim ke webhook: {e}"


def show_chatbot(df_customer):
    st.title("🤖 ChatBot Analisis Customer")

    model_choice = st.selectbox("Gunakan model AI:", ["GPT (OpenAI)", "Gemini (Google)", "Agent N8N"])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Tampilkan history chat
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    # Input chat
    if prompt := st.chat_input("Tanya tentang data customer..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append(("user", prompt))

        with st.chat_message("assistant"):
            with st.spinner("Sedang memproses..."):
                if model_choice == "GPT (OpenAI)":
                    reply = ask_openai_with_data(prompt, df_customer)
                elif model_choice == "Gemini (Google)":
                    reply = ask_gemini_with_data(prompt, df_customer)
                else:
                    reply = send_to_webhook(prompt)

                st.markdown(reply)
                st.session_state.chat_history.append(("assistant", reply))
