import pandas as pd

# === 1. Load data utama ===
mdi_file = "MDI.xlsx"
mdi_df = pd.read_excel(mdi_file, sheet_name="MDI")

# === 2. Buat pivot berdasarkan 'Case' ===
pivot_df = mdi_df.groupby(
    ['Institution', 'Case', 'Case Type', 'Patient', 'Admission Date', 'Payor'],
    as_index=False
).agg({
    'Gross Price': 'sum',
    'Net Value': 'sum'
})

# === 3. Load data pembayaran dari file kedua ===
payment_file = "Data SAP Halodoc.XLSX"
payment_df = pd.read_excel(payment_file)

# Ambil kolom yang dibutuhkan untuk sinkronisasi
payment_cols = ['Case', 'Billing Date', 'Due Date', 'Payment Date', 'Payment Status', 'Days for Payment']
payment_trimmed = payment_df[payment_cols]

# === 4. Gabungkan berdasarkan kolom 'Case' ===
merged_df = pd.merge(pivot_df, payment_trimmed, on='Case', how='left')

# === 5. Simpan hasil gabungan ke file baru ===
output_file = "Hasil_Pivot_Sinkron.xlsx"
merged_df.to_excel(output_file, index=False)

print(f"✅ Selesai! File hasil sinkronisasi disimpan ke: {output_file}")
