import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.schema.runnable import Runnable
from langchain.schema.output_parser import StrOutputParser
import google.generativeai as genai
import requests
import pandas as pd
from typing import Dict, Any

# Setup untuk LangChain
openai_api_key = "YOUR_OPENAI_API_KEY"
gemini_api_key = "YOUR_GEMINI_API_KEY"
webhook_url = "YOUR_WEBHOOK_URL"

# Setup LangChain untuk OpenAI
llm_openai = OpenAI(api_key=openai_api_key, model_name="gpt-3.5-turbo-instruct")

# Setup LangChain untuk Gemini - Custom Runnable class
class GeminiRunnable(Runnable):
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def invoke(self, input_data: Dict[str, Any], config=None) -> str:
        if isinstance(input_data, dict):
            # Extract prompt from dictionary
            prompt = input_data.get("text", str(input_data))
        else:
            prompt = str(input_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "Maaf, tidak ada respons yang dihasilkan."
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def ainvoke(self, input_data: Dict[str, Any], config=None) -> str:
        return self.invoke(input_data, config)
    
    def batch(self, inputs, config=None):
        return [self.invoke(input_data, config) for input_data in inputs]
    
    async def abatch(self, inputs, config=None):
        return [await self.ainvoke(input_data, config) for input_data in inputs]
    
    def stream(self, input_data, config=None):
        yield self.invoke(input_data, config)
    
    async def astream(self, input_data, config=None):
        yield await self.ainvoke(input_data, config)

# Fungsi untuk request Gemini menggunakan LangChain
def ask_gemini_with_langchain(prompt, df):
    df_sample = df.head(10).to_csv(index=False)
    template = """
    Berikut adalah data customer yang diminta:
    {df_sample}
    
    Pertanyaan: {prompt}
    
    Jawab dalam bahasa Indonesia dengan detail dan berikan insight yang berguna.
    """
    
    prompt_template = PromptTemplate(
        input_variables=["df_sample", "prompt"],
        template=template
    )
    
    gemini_runnable = GeminiRunnable()
    
    # Format prompt
    formatted_prompt = prompt_template.format(df_sample=df_sample, prompt=prompt)
    
    # Invoke directly
    response = gemini_runnable.invoke({"text": formatted_prompt})
    return response

# Fungsi untuk request OpenAI menggunakan LangChain
def ask_openai_with_langchain(prompt, df):
    df_sample = df.head(10).to_csv(index=False)
    template = """
    Berikut adalah data customer (10 baris pertama):
    {df_sample}
    
    Sekarang jawab pertanyaan ini:
    {prompt}
    
    Jawab dalam bahasa Indonesia dengan detail dan berikan insight yang berguna.
    """
    
    prompt_template = PromptTemplate(
        input_variables=["df_sample", "prompt"],
        template=template
    )
    
    chain = LLMChain(llm=llm_openai, prompt=prompt_template)
    
    try:
        response = chain.run(df_sample=df_sample, prompt=prompt)
        return response
    except Exception as e:
        return f"Error dengan OpenAI: {str(e)}"

# Fungsi Webhook
def send_to_webhook(prompt):
    try:
        res = requests.post(webhook_url, json={"prompt": prompt}, timeout=30)
        if res.status_code == 200:
            return res.json().get("reply", "No response")
        return f"Error: {res.status_code}"
    except requests.RequestException as e:
        return f"Error webhook: {str(e)}"

# Fungsi alternatif tanpa LangChain untuk Gemini
def ask_gemini_direct(prompt, df):
    """Alternatif jika LangChain bermasalah"""
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        df_sample = df.head(10).to_csv(index=False)
        full_prompt = f"""
        Berikut adalah data customer yang diminta:
        {df_sample}
        
        Pertanyaan: {prompt}
        
        Jawab dalam bahasa Indonesia dengan detail dan berikan insight yang berguna.
        """
        
        response = model.generate_content(full_prompt)
        return response.text if response.text else "Maaf, tidak ada respons yang dihasilkan."
    except Exception as e:
        return f"Error: {str(e)}"

# Contoh utama dengan LangChain dan Streamlit
def show_chatbot(df_customer):
    st.title("🤖 ChatBot Analisis Customer")
    
    # Add option for fallback method
    model_choice = st.selectbox(
        "Gunakan model AI:", 
        ["GPT (OpenAI)", "Gemini (Google)", "Gemini (Direct)", "Agent N8N"]
    )
    
    # Show data preview
    with st.expander("Preview Data Customer"):
        st.dataframe(df_customer.head())
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Tampilkan history chat
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)
    
    # Input chat
    if prompt := st.chat_input("Tanya tentang data customer..."):
        # Add user message to chat
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append(("user", prompt))
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Menganalisis data..."):
                if model_choice == "GPT (OpenAI)":
                    reply = ask_openai_with_langchain(prompt, df_customer)
                elif model_choice == "Gemini (Google)":
                    reply = ask_gemini_with_langchain(prompt, df_customer)
                elif model_choice == "Gemini (Direct)":
                    reply = ask_gemini_direct(prompt, df_customer)
                else:  # Agent N8N
                    reply = send_to_webhook(prompt)
            
            st.markdown(reply)
        
        st.session_state.chat_history.append(("assistant", reply))

# Fungsi untuk testing
def test_models(df_sample):
    st.sidebar.title("🔧 Test Models")
    
    if st.sidebar.button("Test Gemini"):
        try:
            result = ask_gemini_direct("Berapa jumlah customer?", df_sample)
            st.sidebar.success("Gemini: OK")
            st.sidebar.text(result[:100] + "...")
        except Exception as e:
            st.sidebar.error(f"Gemini Error: {str(e)}")
    
    if st.sidebar.button("Test OpenAI"):
        try:
            result = ask_openai_with_langchain("Berapa jumlah customer?", df_sample)
            st.sidebar.success("OpenAI: OK")
            st.sidebar.text(result[:100] + "...")
        except Exception as e:
            st.sidebar.error(f"OpenAI Error: {str(e)}")

# Main function example (tambahkan ini jika diperlukan)
def main():
    # Sample data untuk testing
    if 'df_customer' not in st.session_state:
        # Buat sample data jika belum ada
        sample_data = {
            'customer_id': range(1, 101),
            'name': [f'Customer {i}' for i in range(1, 101)],
            'age': [20 + (i % 60) for i in range(100)],
            'city': ['Jakarta', 'Bandung', 'Surabaya'] * 33 + ['Jakarta'],
            'purchase_amount': [1000 + (i * 50) for i in range(100)]
        }
        st.session_state.df_customer = pd.DataFrame(sample_data)
    
    show_chatbot(st.session_state.df_customer)
    test_models(st.session_state.df_customer)

if __name__ == "__main__":
    main()
