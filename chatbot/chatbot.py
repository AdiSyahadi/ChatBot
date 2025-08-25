import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import google.generativeai as genai
import requests

# Fungsi untuk setup LangChain dan API keys
def setup_langchain(openai_api_key, gemini_api_key):
    # Setup untuk LangChain
    llm_openai = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")

    # Setup LangChain untuk Gemini
    genai.configure(api_key=gemini_api_key)

    return llm_openai

# Fungsi untuk request Gemini menggunakan LangChain
def ask_gemini_with_langchain(prompt):
    template = """
    Berikut adalah data customer yang diminta:

    {df_sample}

    Pertanyaan: {prompt}
    """
    prompt_with_data = PromptTemplate(
        input_variables=["df_sample", "prompt"],
        template=template
    )
    chain = LLMChain(llm=genai.GenerativeModel("models/gemini-1.5-flash"), prompt=prompt_with_data)
    
    response = chain.run(df_sample="Data customer sample", prompt=prompt)
    return response

# Fungsi untuk request OpenAI menggunakan LangChain
def ask_openai_with_langchain(prompt, df, llm_openai):
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

# Fungsi untuk menampilkan chatbot
def show_chatbot(df_customer, openai_api_key, gemini_api_key):
    st.title("🤖 ChatBot Analisis Customer")

    model_choice = st.selectbox("Gunakan model AI:", ["GPT (OpenAI)", "Gemini (Google)"])

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

        # Setup LangChain
        llm_openai = setup_langchain(openai_api_key, gemini_api_key)

        # Gunakan LangChain untuk mengatur alur
        if model_choice == "GPT (OpenAI)":
            reply = ask_openai_with_langchain(prompt, df_customer, llm_openai)
        elif model_choice == "Gemini (Google)":
            reply = ask_gemini_with_langchain(prompt)

        st.markdown(reply)
        st.session_state.chat_history.append(("assistant", reply))
