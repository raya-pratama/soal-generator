import streamlit as st
import google.generativeai as genai
import json

# 1. SETTING HALAMAN & TAMPILAN
st.set_page_config(page_title="AI Exam Generator", page_icon="📝", layout="wide")

# Custom CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stRadio > label { font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. KONEKSI API & AUTO-MODEL
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Mencari model yang tersedia agar tidak 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioritas: 1.5-flash, jika tidak ada baru Pro, jika tidak ada ambil yang pertama
        if 'models/gemini-1.5-flash' in models: selected = 'gemini-1.5-flash'
        elif 'models/gemini-pro' in models: selected = 'gemini-pro'
        else: selected = models[0].replace('models/', '')
        
        model = genai.GenerativeModel(selected)
        st.sidebar.success(f"✅ AI Aktif ({selected})")
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.stop()
else:
    st.error("Masukkan API Key di Secrets!")
    st.stop()

# 3. SIDEBAR (FITUR LENGKAP)
with st.sidebar:
    st.header("⚙️ Pengaturan Soal")
    topik = st.text_area("Materi / Topik:", placeholder="Contoh: OSPF Routing Cisco", height=100)
    col1, col2 = st.columns(2)
    with col1:
        jumlah = st.slider("Jumlah:", 1, 10, 3)
    with col2:
        tingkat = st.selectbox("Level:", ["Dasar", "Menengah", "Mahir"])
    
    tipe = st.selectbox("Tipe Soal:", ["Pilihan Ganda", "Studi Kasus / Praktek"])
    
    st.divider()
    generate_btn = st.button("Generate Soal Sekarang 🚀", use_container_width=True)

# 4. PROSES GENERATE
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal terbaik untukmu..."):
        prompt = f"""
        Buatkan {jumlah} soal {tipe} tentang {topik} tingkat {tingkat}.
        WAJIB memberikan kunci jawaban dan penjelasan.
        Format output HARUS JSON murni:
        {{
          "soal_list": [
            {{
              "tanya": "pertanyaan",
              "opsi": ["A", "B", "C", "D"],
              "kunci": "jawaban benar",
              "info": "penjelasan teknis"
            }}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            txt = response.text.strip()
            # Pembersihan tag JSON
            if "```json" in txt: txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt: txt = txt.split("```")[1].split("```")[0].strip()
            
            st.session_state['data_soal'] = json.loads(txt)['soal_list']
        except Exception as e:
            st.error(f"Gagal memproses soal: {e}")

# 5. DISPLAY SOAL (INTERAKTIF)
st.title("📝 AI Question Generator")
st.write("Gunakan AI untuk membuat soal ujian berkualitas secara instan.")

if 'data_soal' in st.session_state:
    for i, s in enumerate(st.session_state['data_soal']):
        with st.expander(f"Soal Nomor {i+1}", expanded=True):
            st.write(f"### {s['tanya']}")
            
            # Jika Pilihan Ganda
            if "opsi" in s and s["opsi"] and len(s["opsi"]) > 0:
                pilihan = st.radio("Pilih jawaban:", s['opsi'], key=f"r_{i}")
                if st.button(f"Cek Jawaban {i+1}", key=f"b_{i}"):
                    if pilihan == s['kunci']:
                        st.success(f"BENAR! ✅")
                    else:
                        st.error(f"SALAH! Kunci: {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")
            
            # Jika Soal Praktek
            else:
                st.warning("🛠️ Ini soal praktek/studi kasus.")
                if st.button(f"Lihat Solusi {i+1}", key=f"b_{i}"):
                    st.write(f"**Kunci Jawaban:** {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")

    if st.button("🗑️ Hapus Semua"):
        del st.session_state['data_soal']
        st.rerun()
