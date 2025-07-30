import streamlit as st
import os
import requests
from dotenv import load_dotenv
import openai
from openai import OpenAI
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument

# Load API key dari .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
webhook_url = "https://dev-mesondigitalid.app.n8n.cloud/webhook-test/0b353a59-3ad1-420a-b96a-93ebc4ef1f3f"

# Setup client
openai_client = OpenAI(api_key=openai_api_key)
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

def kirim_ke_webhook(prompt, response, model):
    try:
        payload = {
            "prompt": prompt,
            "response": response,
            "model": model
        }
        r = requests.post(webhook_url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Gagal kirim ke webhook: {e}")
        return False

def show_chatbot(df_customer):
    st.title("🤖 ChatBot Analisis Customer")

    model_choice = st.selectbox("Gunakan model AI:", ["GPT (OpenAI)", "Gemini (Google)"])

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
                if model_choice == "GPT (OpenAI)":
                    reply = ask_openai_with_data(prompt, df_customer)
                else:
                    reply = ask_gemini_with_data(prompt, df_customer)

                st.markdown(reply)
                st.session_state.chat_history.append(("assistant", reply))

                # Kirim ke webhook n8n
                berhasil = kirim_ke_webhook(prompt, reply, model_choice)
                if not berhasil:
                    st.warning("⚠️ Gagal mengirim data ke webhook.")

