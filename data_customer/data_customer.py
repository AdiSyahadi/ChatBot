import streamlit as st
from streamlit_autorefresh import st_autorefresh

def show(df_customer):
    st_autorefresh(interval=1000, key="datarefresh")
    st.title("📗 TABEL DATA CUSTOMER")

    st.subheader("⬇️ Export Data Customer")
    selected_cols = st.multiselect(
        "Pilih kolom yang ingin diekspor:",
        options=df_customer.columns.tolist(),
        default=df_customer.columns.tolist()
    )

    if selected_cols:
        export_df = df_customer[selected_cols].drop_duplicates().dropna(how="all")
        st.download_button(
            label="💾 Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="data_customer_terpilih.csv",
            mime="text/csv"
        )

    st.dataframe(df_customer, use_container_width=True)
