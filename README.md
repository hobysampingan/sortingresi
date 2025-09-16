# PDF Resi Sorter

Aplikasi Streamlit untuk memproses dan mengurutkan file PDF berisi banyak resi berdasarkan Seller SKU.

## Fitur

- **Ekstraksi Otomatis**: Mengidentifikasi Order ID dan Seller SKU dari teks PDF
- **Pengelompokan**: Mengelompokkan halaman berdasarkan Order ID yang sama
- **Pengurutan**: Mengurutkan ulang PDF berdasarkan Seller SKU
- **Antarmuka Web**: Mudah digunakan melalui browser
- **Download**: Hasil pengurutan dapat diunduh sebagai PDF baru

## Cara Penggunaan

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan Aplikasi**:
   ```bash
   streamlit run app.py
   ```

3. **Buka Browser**:
   - Kunjungi `http://localhost:8501`
   - Upload file PDF yang berisi resi
   - Aplikasi akan otomatis memproses dan mengurutkan
   - Download hasilnya sebagai PDF yang telah diurutkan

## Struktur Kode

- `app.py`: Aplikasi utama Streamlit
- `requirements.txt`: Dependencies Python
- `test.py`: Script untuk testing fungsi ekstraksi
- `sample_resi.pdf`: Contoh file PDF untuk testing

## Algoritma Pengurutan

1. **Ekstraksi Teks**: Menggunakan pdfplumber untuk mengekstrak teks dari setiap halaman
2. **Deteksi Order ID**: Mencari pola "Order ID: [angka]" di teks
3. **Deteksi Seller SKU**: Mencari pola SKU seperti "DM-XXXX" atau "ELIA-XXXX"
4. **Pengelompokan**: Mengelompokkan halaman berdasarkan Order ID
5. **Penanganan Multi-Halaman**: Untuk resi dengan beberapa halaman, hanya menggunakan SKU dari halaman pertama untuk pengurutan, halaman berikutnya tetap bersama halaman pertama
6. **Pengurutan**: Mengurutkan berdasarkan Seller SKU secara alfabetis
7. **Pembuatan PDF Baru**: Membuat PDF baru dengan urutan halaman yang telah diurutkan

## Contoh Output

Dari PDF dengan 212 halaman, aplikasi dapat mengelompokkannya menjadi:
- DM-TARO: 157 halaman
- DM-SORA: 26 halaman
- DM-LILY: 8 halaman
- DM-FILLA: 8 halaman
- DM-MINO: 4 halaman
- DM-TALI: 3 halaman
- Dan lainnya...

## Error Handling

Aplikasi dilengkapi dengan error handling untuk:
- File PDF yang tidak dapat diproses
- Halaman tanpa Order ID atau SKU
- Masalah dalam pembuatan PDF baru

## Teknologi

- **Streamlit**: Framework web untuk aplikasi Python
- **pdfplumber**: Library untuk ekstraksi teks dari PDF
- **PyPDF2**: Library untuk manipulasi PDF
- **re**: Regular expressions untuk pencarian pola
