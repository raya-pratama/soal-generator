import streamlit as st
import google.generativeai as genai
import json

# 1. SETTING HALAMAN
st.set_page_config(page_title="AI Exam Maker", page_icon="📝")
st.title("📝 AI Question Generator")

# 2. KONFIGURASI API & MODEL
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Logika memilih model secara otomatis (Fallback)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if 'models/gemini-1.5-flash' in available_models:
            model_name = 'gemini-1.5-flash'
        else:
            model_name = 'gemini-pro'
            
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Koneksi ke Google AI Gagal: {e}")
        st.stop()
else:
    st.error("❌ API Key tidak ditemukan di Secrets!")
    st.stop()

# 3. INPUT USER
with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_area("Topik Materi:", placeholder="Contoh: Dasar-dasar Routing Cisco")
    jumlah = st.slider("Jumlah Soal:", 1, 10, 3)
    tingkat = st.selectbox("Kesulitan:", ["Dasar", "Menengah", "Lanjut"])
    tipe = st.selectbox("Jenis:", ["Pilihan Ganda", "Praktek"])
    generate_btn = st.button("Generate Soal 🚀")

# 4. PROSES AI
if generate_btn and topik:
    with st.spinner(f"Sedang membuat soal menggunakan {model_name}..."):
        prompt = f"""
        Buat {jumlah} soal {tipe} tentang {topik} tingkat {tingkat}.
        Output harus JSON murni:
        {{
          "list_soal": [
            {{
              "tanya": "...",
              "opsi": ["A", "B", "C", "D"],
              "kunci": "...",
              "info": "..."
            }}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            res_text = response.text
            # Pembersihan JSON
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            st.session_state['data_soal'] = json.loads(res_text)['list_soal']
        except Exception as e:
            st.error(f"Error: {e}")

# 5. TAMPILKAN SOAL
if 'data_soal' in st.session_state:
    for i, s in enumerate(st.session_state['data_soal']):
        st.subheader(f"Soal {i+1}")
        st.write(s['tanya'])
        
        if "opsi" in s and s["opsi"]:
            ans = st.radio("Pilih jawaban:", s['opsi'], key=f"q_{i}")
            if st.button(f"Cek Jawaban {i+1}"):
                if ans == s['kunci']:
                    st.success("Benar! 🎉")
                else:
                    st.error(f"Salah. Jawaban: {s['kunci']}")
                st.info(f"Penjelasan: {s['info']}")
        st.divider()
