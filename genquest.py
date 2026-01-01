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

# 4. LOGIKA GENERATE (VERSI ANTI-ERROR)
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal praktek..."):
        # Memberikan batasan agar AI tidak bicara terlalu panjang yang memicu "Unterminated String"
        if tipe == "Pilihan Ganda":
            instruction = "Buatkan soal pilihan ganda dengan 4 opsi. Berikan penjelasan singkat."
        else:
            instruction = """Buatkan soal PRAKTEK/LAB. 
            Fokus pada skenario konfigurasi. 
            Sajikan solusi CLI secara ringkas dan padat."""

        prompt = f"""
        Instruktur IT: {instruction}
        Topik: {topik} | Level: {tingkat} | Jumlah: {jumlah}
        
        WAJIB OUTPUT JSON MURNI:
        {{
          "soal_list": [
            {{
              "tanya": "skenario",
              "opsi": [], 
              "kunci": "langkah CLI ringkas",
              "info": "konsep"
            }}
          ]
        }}
        JANGAN memutus kalimat. Jika jawaban panjang, gunakan poin-poin singkat.
        """
        
        try:
            # Gunakan parameter tambahan untuk mengontrol kreativitas (temperature)
            response = model.generate_content(prompt, generation_config={"temperature": 0.2})
            txt = response.text.strip()
            
            # Pembersihan JSON yang lebih kuat
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0].strip()
            
            # Perbaikan otomatis untuk karakter newline yang sering merusak JSON
            txt = txt.replace('\n', ' ') 
            
            data_json = json.loads(txt)
            st.session_state['data_soal'] = data_json['soal_list']
            st.session_state['tipe_aktif'] = tipe
            st.rerun() # Refresh untuk menampilkan hasil
            
        except json.JSONDecodeError as je:
            st.error(f"Format data dari AI tidak sempurna. Coba klik tombol Generate lagi.")
            st.debug(f"Detail error: {je}")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
# --- 5. DISPLAY SOAL (VERSI AMAN) ---
st.title("📝 AI Question Generator")

if 'data_soal' in st.session_state:
    # Cek apakah tipe_aktif ada, jika tidak ada beri nilai default
    tipe_sekarang = st.session_state.get('tipe_aktif', 'Pilihan Ganda')
    
    for i, s in enumerate(st.session_state['data_soal']):
        with st.expander(f"Soal Nomor {i+1}", expanded=True):
            st.write(f"### Pertanyaan/Skenario:")
            st.write(s['tanya'])
            
            # Tampilan jika Pilihan Ganda (Menggunakan variabel tipe_sekarang yang aman)
            if tipe_sekarang == "Pilihan Ganda" and s.get('opsi'):
                pilihan = st.radio("Pilih jawaban:", s['opsi'], key=f"r_{i}")
                if st.button(f"Cek Jawaban {i+1}", key=f"b_{i}"):
                    if pilihan == s['kunci']: 
                        st.success(f"BENAR! ✅")
                    else: 
                        st.error(f"SALAH! Kunci: {s['kunci']}")
                    st.info(f"**Penjelasan:** {s['info']}")
            
            # Tampilan jika Praktek
            else:
                st.info("🛠️ **Tugas Praktek:** Kerjakan skenario di atas pada simulator (Cisco Packet Tracer/GNS3).")
                if st.button(f"Lihat Kunci Konfigurasi {i+1}", key=f"b_{i}"):
                    st.markdown("### 🔑 Solusi / Langkah Konfigurasi:")
                    # Menampilkan CLI dengan format code block agar rapi
                    st.code(s['kunci'], language="bash") 
                    st.info(f"**Konsep Dasar:** {s['info']}")

    if st.button("🗑️ Hapus & Reset"):
        # Menghapus semua state agar bersih kembali
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
