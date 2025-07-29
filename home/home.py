# home.py
import streamlit as st

def show():
    st.markdown('<div class="meslon-title">System Meslon Digital</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Selamat datang di sistem dashboard & layanan interaktif</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(
            "https://plus.unsplash.com/premium_photo-1680777484547-de735ff024a4?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        ### Apa itu Meslon Digital?

        Meslon Digital adalah platform monitoring data dan interaksi digital yang memudahkan Anda melihat informasi penting dengan cepat dan modern.

        **Fitur:**
        - Visualisasi data otomatis  
        - Integrasi Google Sheets  
        - ChatBot untuk interaksi dasar  
        """, unsafe_allow_html=True)
