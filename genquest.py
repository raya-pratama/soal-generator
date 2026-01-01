import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="AI Generator Soal", layout="centered")
st.title("📝 AI Question Generator")

# --- KONEKSI API & CEK MODEL ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # MENGAMBIL DAFTAR MODEL YANG TERSEDIA UNTUK KEY KAMU
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            st.error("Tidak ada model yang tersedia untuk API Key ini.")
            st.stop()
            
        # Pilih model pertama yang tersedia (biasanya yang paling stabil)
        model_name = models[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
        st.caption(f"✅ Sistem Aktif | Model: {model_name}")
        
    except Exception as e:
        st.error(f"Gagal Inisialisasi: {e}")
        st.stop()
else:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

# --- INPUT USER ---
topik = st.text_input("Topik Materi (Contoh: DHCP Cisco):")
if st.button("Buat Soal 🚀") and topik:
    with st.spinner("AI sedang merancang soal..."):
        prompt = f"Buatkan 3 soal pilihan ganda tentang {topik}. Format JSON murni: {{\"soal\": [{{\"tanya\": \"..\", \"opsi\": [\"A\",\"B\",\"C\",\"D\"], \"kunci\": \"..\", \"info\": \"..\"}}]}}"
        
        try:
            response = model.generate_content(prompt)
            # Membersihkan output
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            st.session_state['data'] = json.loads(text)['soal']
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- TAMPILAN ---
if 'data' in st.session_state:
    for i, s in enumerate(st.session_state['data']):
        st.write(f"**{i+1}. {s['tanya']}**")
        ans = st.radio(f"Pilih {i+1}:", s['opsi'], key=f"q{i}")
        if st.button(f"Cek No {i+1}", key=f"b{i}"):
            if ans == s['kunci']: st.success("Benar!")
            else: st.error(f"Salah! Kunci: {s['kunci']}")
            st.info(f"Penjelasan: {s['info']}")
