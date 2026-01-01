import streamlit as st
import google.generativeai as genai
import json

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="AI Exam Maker", page_icon="📝", layout="centered")

# 2. SISTEM KEAMANAN (SECRETS)
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Gunakan gemini-1.5-flash sebagai utama, jika gagal sistem akan otomatis handle
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Koneksi AI Gagal: {e}")
        st.stop()
else:
    st.error("❌ API Key tidak ditemukan! Masukkan GEMINI_API_KEY di Settings > Secrets.")
    st.stop()

# 3. ANTARMUKA UTAMA
st.title("📝 AI Question Generator")
st.write("Buat soal latihan otomatis hanya dengan menuliskan topiknya.")

with st.sidebar:
    st.header("⚙️ Pengaturan Soal")
    topik = st.text_area("Masukkan Topik/Materi:", placeholder="Contoh: Konfigurasi Static Routing Cisco Packet Tracer", height=150)
    jumlah = st.slider("Jumlah Soal:", 1, 10, 3)
    tingkat = st.selectbox("Tingkat Kesulitan:", ["Dasar", "Menengah", "Lanjut"])
    tipe = st.selectbox("Tipe Soal:", ["Pilihan Ganda", "Case Study / Praktek"])
    
    generate_btn = st.button("Buat Soal Sekarang 🚀")

# 4. LOGIKA GENERATOR
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal..."):
        # Prompt yang diperketat agar AI selalu membalas dengan JSON murni
        prompt = f"""
        Bertindaklah sebagai instruktur IT ahli. Buatlah {jumlah} soal {tipe} tentang {topik} tingkat {tingkat}.
        WAJIB memberikan jawaban benar dan penjelasan teknis yang akurat.
        
        FORMAT OUTPUT HARUS JSON MURNI (tanpa teks pembuka/penutup):
        {{
          "list_soal": [
            {{
              "tanya": "teks pertanyaan",
              "opsi": ["A", "B", "C", "D"],
              "kunci": "isi jawaban yang benar",
              "info": "penjelasan singkat"
            }}
          ]
        }}
        """
        
        try:
            response = model.generate_content(prompt)
            # Pembersihan string JSON dari tag markdown (```json ... ```)
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            # Parsing JSON ke Python Dictionary
            data_hasil = json.loads(res_text)
            st.session_state['data_kuis'] = data_hasil['list_soal']
            st.success("Berhasil membuat soal!")
            
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")
            st.info("Tips: Coba klik tombol 'Buat Soal' sekali lagi jika terjadi error timeout.")

# 5. TAMPILAN SOAL & CEK JAWABAN
if 'data_kuis' in st.session_state:
    st.divider()
    for idx, s in enumerate(st.session_state['data_kuis']):
        with st.container():
            st.markdown(f"### Soal {idx+1}")
            st.write(s['tanya'])
            
            # Logika Pilihan Ganda
            if "opsi" in s and s["opsi"] and len(s["opsi"]) > 0:
                user_ans = st.radio(f"Pilih jawaban untuk nomor {idx+1}:", s['opsi'], key=f"ans_{idx}")
                
                if st.button(f"Cek Jawaban No {idx+1}", key=f"btn_{idx}"):
                    if user_ans == s['kunci']:
                        st.success(f"Tepat sekali! ✅")
                    else:
                        st.error(f"Kurang tepat. Jawaban benar: {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")
            
            # Logika Case Study (Praktek)
            else:
                st.info("💡 Ini adalah soal praktek. Kerjakan di simulator Anda.")
                if st.button(f"Lihat Kunci & Langkah No {idx+1}", key=f"btn_{idx}"):
                    st.write(f"**Jawaban/Langkah:** {s['kunci']}")
                    st.write(f"**Tips:** {s['info']}")
            
            st.divider()

    if st.button("🗑️ Hapus & Buat Baru"):
        del st.session_state['data_kuis']
        st.rerun()

st.caption("AI Trader & Exam Maker © 2024 - Menggunakan Google Gemini API")
