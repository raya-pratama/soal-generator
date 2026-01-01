import streamlit as st
import google.generativeai as genai
import json

# --- KONFIGURASI KEAMANAN ---
# Mengambil API Key dari Streamlit Secrets
try:
    # Kita menyuruh Streamlit mencari laci bernama "GEMINI_API_KEY"
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("❌ Key 'GEMINI_API_KEY' tidak ditemukan di Settings aplikasi!")
    st.stop()

# --- TAMPILAN ---
st.set_page_config(page_title="AI Exam Maker", page_icon="📝")
st.title("📝 AI Question Generator")
st.write("Buat soal latihan Cisco, Koding, atau Teori apapun secara otomatis.")

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_area("Detail Materi/Topik:", placeholder="Contoh: Konfigurasi Static Routing di Cisco Packet Tracer")
    jumlah = st.slider("Jumlah Soal:", 1, 10, 3)
    tingkat = st.selectbox("Tingkat Kesulitan:", ["Dasar", "Menengah", "Lanjut"])
    tipe = st.selectbox("Tipe Soal:", ["Pilihan Ganda", "Soal Praktek/Case Study"])
    
    generate_btn = st.button("Buat Soal Sekarang 🚀")

# --- PROMPT LOGIC ---
if generate_btn and topik:
    with st.spinner("AI sedang berpikir..."):
        prompt = f"""
        Bertindaklah sebagai instruktur ahli. Buatlah {jumlah} soal {tipe} tentang {topik} tingkat {tingkat}.
        WAJIB berikan jawaban benar dan penjelasan teknisnya.
        Format output HARUS JSON murni:
        {{
          "list_soal": [
            {{
              "tanya": "pertanyaan",
              "opsi": ["A", "B", "C", "D"],
              "kunci": "jawaban benar",
              "info": "penjelasan"
            }}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            # Membersihkan tag markdown jika ada
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            st.session_state['data_kuis'] = json.loads(clean_text)['list_soal']
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")

# --- DISPLAY SOAL ---
if 'data_kuis' in st.session_state:
    for idx, s in enumerate(st.session_state['data_kuis']):
        with st.expander(f"Soal {idx+1}: {s['tanya'][:50]}...", expanded=True):
            st.write(f"**{s['tanya']}**")
            
            if "opsi" in s and s["opsi"]:
                user_ans = st.radio(f"Pilih jawaban:", s['opsi'], key=f"ans_{idx}")
                if st.button(f"Cek Jawaban #{idx+1}"):
                    if user_ans == s['kunci']:
                        st.success(f"Tepat! Jawaban: {s['kunci']}")
                    else:
                        st.error(f"Kurang tepat. Jawaban benar: {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")
            else:
                # Untuk soal praktek tanpa pilihan ganda
                st.warning("Tipe Praktek: Silakan kerjakan di simulator, lalu klik kunci untuk verifikasi.")
                if st.button(f"Lihat Kunci Praktek #{idx+1}"):
                    st.write(f"**Langkah/Jawaban:** {s['kunci']}")
                    st.info(f"**Tips:** {s['info']}")

    if st.button("Reset / Buat Baru"):
        del st.session_state['data_kuis']
        st.rerun()
