import streamlit as st
import google.generativeai as genai

# 1. KONFIGURASI DASAR
st.set_page_config(page_title="AI Generator Soal", layout="centered")
st.title("📝 AI Question Generator (Pro)")

# 2. KONEKSI API
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Mencari model yang tersedia secara otomatis
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = available_models[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.stop()
else:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

# 3. INPUT USER
with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_input("Topik (Contoh: VLAN Cisco):")
    tipe = st.radio("Tipe Soal:", ["Pilihan Ganda", "Praktek / Lab"])
    generate_btn = st.button("Generate Soal 🚀")

# 4. LOGIKA GENERATE (TANPA JSON - ANTI ERROR)
if generate_btn and topik:
    with st.spinner("AI sedang menulis soal..."):
        # Kita minta AI menulis dengan pemisah khusus "###"
        prompt = f"""
        Buatkan 1 soal {tipe} tentang {topik}.
        Tuliskan dengan format persis seperti ini:
        PERTANYAAN: (isi pertanyaan di sini)
        ###
        JAWABAN: (isi kunci jawaban atau langkah CLI di sini)
        ###
        PENJELASAN: (isi penjelasan singkat di sini)
        """
        
        try:
            response = model.generate_content(prompt)
            hasil_teks = response.text
            
            # Memotong teks berdasarkan pemisah ###
            bagian = hasil_teks.split("###")
            
            if len(bagian) >= 3:
                st.session_state['soal'] = bagian[0].replace("PERTANYAAN:", "").strip()
                st.session_state['kunci'] = bagian[1].replace("JAWABAN:", "").strip()
                st.session_state['info'] = bagian[2].replace("PENJELASAN:", "").strip()
                st.session_state['tipe_lalu'] = tipe
            else:
                st.error("AI memberikan format yang salah, coba klik Generate lagi.")
        except Exception as e:
            st.error(f"Kesalahan: {e}")

# 5. TAMPILAN
if 'soal' in st.session_state:
    st.divider()
    st.subheader("📋 Pertanyaan")
    st.write(st.session_state['soal'])
    
    if st.button("Tampilkan Jawaban & Solusi"):
        st.success("✅ Kunci Jawaban / Langkah Konfigurasi:")
        # Jika tipe praktek, tampilkan sebagai kode CLI
        if st.session_state.get('tipe_lalu') == "Praktek / Lab":
            st.code(st.session_state['kunci'], language="bash")
        else:
            st.write(st.session_state['kunci'])
            
        st.info(f"**Penjelasan Konsep:**\n{st.session_state['info']}")

    if st.button("Hapus"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
