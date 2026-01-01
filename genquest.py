import streamlit as st
import google.generativeai as genai
import json

# 1. KONFIGURASI
st.set_page_config(page_title="AI Exam Generator", page_icon="📝", layout="wide")

# 2. API & MODEL
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else 'gemini-pro'
        model = genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.stop()
else:
    st.error("API Key belum diset di Secrets!")
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_area("Topik Materi:", placeholder="Contoh: Konfigurasi EIGRP Cisco", height=100)
    jumlah = st.slider("Jumlah Soal:", 1, 5, 2)
    tipe = st.radio("Tipe Soal:", ["Pilihan Ganda", "Praktek / Studi Kasus"])
    generate_btn = st.button("Generate Soal 🚀", use_container_width=True)

# 4. LOGIKA GENERATE
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal..."):
        # Prompt lebih ketat agar JSON tidak rusak
        if tipe == "Pilihan Ganda":
            instruction = "Buat soal pilihan ganda (A,B,C,D)."
        else:
            instruction = "Buat soal LAB PRAKTEK. Kunci jawaban berisi urutan perintah CLI yang lengkap."

        prompt = f"""
        Instruktur IT: {instruction}
        Topik: {topik} | Jumlah: {jumlah}
        
        WAJIB JSON MURNI:
        {{
          "soal_list": [
            {{
              "tanya": "pertanyaan",
              "opsi": ["A", "B", "C", "D"],
              "kunci": "jawaban",
              "info": "penjelasan"
            }}
          ]
        }}
        Catatan: Gunakan escape character untuk tanda kutip di dalam string. JANGAN memutus JSON.
        """
        
        try:
            response = model.generate_content(prompt)
            txt = response.text.strip()
            
            # Pembersihan JSON yang lebih aman
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0].strip()
            
            # Parsing JSON
            data_json = json.loads(txt)
            st.session_state['data_soal'] = data_json['soal_list']
            st.session_state['tipe_aktif'] = tipe
            st.rerun()
            
        except Exception as e:
            st.error("⚠️ AI memberikan format data yang tidak stabil. Silakan klik 'Generate' lagi.")
            # st.exception(e) # Aktifkan ini jika ingin melihat detail error asli

# 5. DISPLAY
st.title("📝 AI Question Generator")

if 'data_soal' in st.session_state:
    tipe_sekarang = st.session_state.get('tipe_aktif', 'Pilihan Ganda')
    
    for i, s in enumerate(st.session_state['data_soal']):
        with st.expander(f"Soal Nomor {i+1}", expanded=True):
            st.write(f"**Pertanyaan:**\n{s['tanya']}")
            
            if tipe_sekarang == "Pilihan Ganda" and s.get('opsi'):
                ans = st.radio("Pilih jawaban:", s['opsi'], key=f"ans_{i}")
                if st.button(f"Cek Jawaban {i+1}", key=f"btn_{i}"):
                    if ans == s['kunci']: st.success("Benar! ✅")
                    else: st.error(f"Salah! Kunci: {s['kunci']}")
                    st.info(f"**Info:** {s['info']}")
            else:
                st.info("🛠️ **Skenario Lab:** Kerjakan pada simulator.")
                if st.button(f"Lihat Kunci Konfigurasi {i+1}", key=f"btn_{i}"):
                    st.code(s['kunci'], language="bash")
                    st.info(f"**Info:** {s['info']}")

    if st.button("🗑️ Reset"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
