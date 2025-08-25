import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import google.generativeai as genai
import requests
import pandas as pd

# Setup untuk LangChain
openai_api_key = "YOUR_OPENAI_API_KEY"
gemini_api_key = "YOUR_GEMINI_API_KEY"
webhook_url = "YOUR_WEBHOOK_URL"

# Setup LangChain untuk OpenAI
llm_openai = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")

# Setup LangChain untuk Gemini
genai.configure(api_key=gemini_api_key)

# Fungsi untuk request Gemini menggunakan API langsung
def ask_gemini(prompt, df):
    df_sample = df.head(10).to_csv(index=False)
    response = genai.GenerativeModel("models/gemini-1.5-flash").generate_content(f"""
    Berikut adalah data customer yang diminta:

    {df_sample}

    Pertanyaan: {prompt}
    """)
    return response.text

# Fungsi untuk request OpenAI menggunakan LangChain
def ask_openai_with_langchain(prompt, df):
    df_sample = df.head(10).to_csv(index=False)
    template = """
    Berikut adalah data customer (10 baris pertama):
    {df_sample}

    Sekarang jawab pertanyaan ini:
    {prompt}
    """
    prompt_with_data = PromptTemplate(
        input_variables=["df_sample", "prompt"],
        template=template
    )
    chain = LLMChain(llm=llm_openai, prompt=prompt_with_data)
    
    response = chain.run(df_sample=df_sample, prompt=prompt)
    return response

# Fungsi Webhook dengan LangChain
def send_to_webhook(prompt):
    res = requests.post(webhook_url, json={"prompt": prompt})
    if res.status_code == 200:
        return res.json().get("reply", "No response")
    return f"Error: {res.status_code}"

# Contoh utama dengan LangChain dan Streamlit
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

        # Gunakan LangChain untuk mengatur alur
        if model_choice == "GPT (OpenAI)":
            reply = ask_openai_with_langchain(prompt, df_customer)
        elif model_choice == "Gemini (Google)":
            reply = ask_gemini(prompt, df_customer)
        else:
            reply = send_to_webhook(prompt)

        st.markdown(reply)
        st.session_state.chat_history.append(("assistant", reply))
