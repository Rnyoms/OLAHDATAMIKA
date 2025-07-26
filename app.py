import streamlit as st
import pandas as pd
from io import BytesIO

# =============================
# 🔐 LOGIN SEDERHANA
# =============================
USER_CREDENTIALS = {
    "regyana": "rahmasari"
}

def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.sidebar.error("❌ Username atau password salah")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# =============================
# 🌐 APLIKASI UTAMA STREAMLIT
# =============================

st.title("🏥 Pivot & Sinkronisasi Pembayaran Rumah Sakit")

st.markdown("""
Silakan upload dua file berikut:
- **File 1:** `MDI.xlsx` (data billing rumah sakit)
- **File 2:** File SAP pembayaran (misal: `Data SAP Halodoc ...`)
""")

mdi_file = st.file_uploader("📤 Upload File MDI (Billing)", type=["xlsx"])
payment_file = st.file_uploader("📤 Upload File SAP (Pembayaran)", type=["xlsx"])

if mdi_file and payment_file:
    try:
        # === BACA FILE ===
        mdi_df = pd.read_excel(mdi_file, sheet_name="MDI")
        payment_df = pd.read_excel(payment_file)

        # === PIVOT DATA ===
        pivot_df = mdi_df.groupby(
            ['Institution', 'Case', 'Case Type', 'Patient', 'Admission Date', 'Payor'],
            as_index=False
        ).agg({
            'Gross Price': 'sum',
            'Net Value': 'sum'
        })

        # === SINKRONISASI DATA ===
        payment_cols = ['Case', 'Billing Date', 'Due Date', 'Payment Date', 'Payment Status', 'Days for Payment']
        payment_trimmed = payment_df[payment_cols]
        merged_df = pd.merge(pivot_df, payment_trimmed, on='Case', how='left')

        # === TAMPILKAN TABEL ===
        st.success(f"✅ Login berhasil! Selamat datang, {st.session_state.username}")
        st.subheader("📊 Hasil Sinkronisasi Data")
        st.dataframe(merged_df)

        # === KONVERSI EXCEL (perbaikan to_excel) ===
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Pivot-Sinkron')
            processed_data = output.getvalue()
            return processed_data

        excel_data = convert_df(merged_df)

        # === TOMBOL DOWNLOAD ===
        st.download_button(
            label="📥 Download Hasil Sinkronisasi",
            data=excel_data,
            file_name="Hasil_Pivot_Sinkron.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Terjadi error saat memproses file: {e}")
