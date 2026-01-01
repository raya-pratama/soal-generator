import streamlit as st
import google.generativeai as genai
import json

# 1. SETTING HALAMAN
st.set_page_config(page_title="AI Exam Generator", page_icon="📝", layout="wide")

# 2. KONEKSI API & AUTO-MODEL
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in models: selected = 'gemini-1.5-flash'
        elif 'models/gemini-pro' in models: selected = 'gemini-pro'
        else: selected = models[0].replace('models/', '')
        model = genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.stop()
else:
    st.error("Masukkan API Key di Secrets!")
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ Pengaturan Soal")
    topik = st.text_area("Materi / Topik:", placeholder="Contoh: OSPF Routing Cisco", height=100)
    jumlah = st.slider("Jumlah Soal:", 1, 5, 2)
    tingkat = st.selectbox("Level:", ["Dasar", "Menengah", "Mahir"])
    tipe = st.radio("Tipe Soal:", ["Pilihan Ganda", "Praktek / Studi Kasus"])
    
    st.divider()
    generate_btn = st.button("Generate Soal Sekarang 🚀", use_container_width=True)

# 4. LOGIKA GENERATE
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal praktek..."):
        # Logika Prompt Berdasarkan Tipe
        if tipe == "Pilihan Ganda":
            instruction = "Buatkan soal pilihan ganda dengan 4 opsi (A, B, C, D)."
        else:
            instruction = """Buatkan soal PRAKTEK/STUDI KASUS murni. 
            JANGAN berikan pilihan ganda. 
            Berikan skenario masalah, tujuan konfigurasi, dan instruksi langkah demi langkah. 
            Kunci jawaban harus berisi urutan perintah (CLI) atau solusi teknis detail."""

        prompt = f"""
        Bertindaklah sebagai instruktur IT senior. {instruction}
        Buatkan {jumlah} soal tentang {topik} tingkat {tingkat}.
        
        Format output HARUS JSON murni:
        {{
          "soal_list": [
            {{
              "tanya": "isi pertanyaan atau skenario lab",
              "opsi": [], 
              "kunci": "langkah konfigurasi atau jawaban benar",
              "info": "penjelasan konsep"
            }}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            txt = response.text.strip()
            if "```json" in txt: txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt: txt = txt.split("```")[1].split("```")[0].strip()
            
            st.session_state['data_soal'] = json.loads(txt)['soal_list']
            st.session_state['tipe_aktif'] = tipe
        except Exception as e:
            st.error(f"Gagal memproses soal: {e}")

# 5. DISPLAY SOAL
st.title("📝 AI Question Generator")

if 'data_soal' in st.session_state:
    for i, s in enumerate(st.session_state['data_soal']):
        with st.expander(f"Soal Nomor {i+1}", expanded=True):
            st.write(f"### Pertanyaan/Skenario:")
            st.write(s['tanya'])
            
            # Tampilan jika Pilihan Ganda
            if st.session_state['tipe_aktif'] == "Pilihan Ganda" and s.get('opsi'):
                pilihan = st.radio("Pilih jawaban:", s['opsi'], key=f"r_{i}")
                if st.button(f"Cek Jawaban {i+1}", key=f"b_{i}"):
                    if pilihan == s['kunci']: st.success(f"BENAR! ✅")
                    else: st.error(f"SALAH! Kunci: {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")
            
            # Tampilan jika Praktek
            else:
                st.info("🛠️ **Tugas Praktek:** Kerjakan skenario di atas pada simulator (Cisco Packet Tracer/GNS3).")
                if st.button(f"Lihat Kunci Konfigurasi {i+1}", key=f"b_{i}"):
                    st.markdown("### 🔑 Solusi / Langkah Konfigurasi:")
                    st.code(s['kunci']) # Menggunakan format code agar CLI rapi
                    st.info(f"**Konsep Dasar:** {s['info']}")

    if st.button("🗑️ Hapus & Reset"):
        del st.session_state['data_soal']
        st.rerun()
