import streamlit as st
import google.generativeai as genai
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Soal Generator", page_icon="📝")
st.title("📝 AI Question Generator")

# --- KONEKSI API ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Menggunakan gemini-pro karena paling stabil dan jarang error 404
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.stop()
else:
    st.error("API Key tidak ditemukan di Secrets!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_input("Topik Materi:", placeholder="Contoh: VLAN Cisco")
    jumlah = st.slider("Jumlah Soal:", 1, 5, 3)
    generate_btn = st.button("Buat Soal 🚀")

# --- LOGIKA GENERATE ---
if generate_btn and topik:
    with st.spinner("AI sedang bekerja..."):
        prompt = f"""
        Buat {jumlah} soal pilihan ganda tentang {topik}.
        Berikan jawaban dan penjelasan.
        Format harus JSON:
        {{
          "list": [
            {{"tanya": "..", "opsi": ["A", "B", "C", "D"], "kunci": "..", "info": ".."}}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            # Membersihkan teks agar hanya mengambil bagian JSON
            teks_asli = response.text
            mulai = teks_asli.find('{')
            akhir = teks_asli.rfind('}') + 1
            json_clean = teks_asli[mulai:akhir]
            
            st.session_state['soal_ai'] = json.loads(json_clean)['list']
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")
            st.info("Coba klik tombol 'Buat Soal' lagi.")

# --- TAMPILAN SOAL ---
if 'soal_ai' in st.session_state:
    for i, s in enumerate(st.session_state['soal_ai']):
        st.write(f"**{i+1}. {s['tanya']}**")
        pilihan = st.radio(f"Pilih jawaban {i+1}:", s['opsi'], key=f"user_{i}")
        
        if st.button(f"Cek Nomor {i+1}", key=f"cek_{i}"):
            if pilihan == s['kunci']:
                st.success("Benar! 🎉")
            else:
                st.error(f"Salah. Kunci: {s['kunci']}")
            st.info(f"Info: {s['info']}")
        st.divider()

    if st.button("Hapus Semua"):
        del st.session_state['soal_ai']
        st.rerun()
