import streamlit as st
import google.generativeai as genai
import time

# 1. KONFIGURASI DASAR
st.set_page_config(page_title="AI Generator Soal", layout="centered")
st.title("📝 AI Question Generator (Visual Edition)")

# 2. KONEKSI API
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = models[0].replace('models/', '')
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
    topik = st.text_input("Topik (Contoh: Static Route Cisco):")
    tipe = st.radio("Tipe Soal:", ["Pilihan Ganda", "Praktek / Lab"])
    # Gunakan key unik untuk tombol generate
    generate_btn = st.button("Generate Soal 🚀", key="main_generate_btn")

# 4. LOGIKA GENERATE (PROMPT DIPERBAIKI)
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal..."):
        # Instruksi spesifik agar pilihan ganda tidak hilang
        if tipe == "Pilihan Ganda":
            detail_instruksi = "Buat soal pilihan ganda dengan 4 opsi (A, B, C, D) di bagian [PERTANYAAN]."
        else:
            detail_instruksi = "Buat soal LAB PRAKTEK tanpa pilihan ganda. Fokus pada skenario konfigurasi."

        prompt = f"""
        Bertindaklah sebagai instruktur Ahli di Bidang Jaringan.
        Tugas: Buat 1 soal {tipe} tentang {topik}.
        
        WAJIB GUNAKAN FORMAT INI:
        
        [TOPOLOGI]
        (Jika praktek, Gambarkan diagram kabel/koneksi antar perangkat menggunakan ASCII. jika pilihan ganda tidak usah)
        
        [PERTANYAAN]
        (Tuliskan soalnya di sini. {detail_instruksi})
        
        [JAWABAN]
        (Jika Pilihan Ganda, tulis huruf jawabannya saja. Jika Praktek, tulis perintah CLI-nya.)
        
        [PENJELASAN]
        (Berikan penjelasan teknis singkat kenapa jawaban itu benar)
        """
        
        try:
            response = model.generate_content(prompt)
            txt = response.text
            
            def ambil_bagian(tag, teks):
                try:
                    # Mencari teks di antara [TAG] dan [TAG berikutnya]
                    return teks.split(f"[{tag}]")[1].split("[")[0].strip()
                except:
                    return f"Data {tag} tidak tersedia."

            st.session_state['vis_topologi'] = ambil_bagian("TOPOLOGI", txt)
            st.session_state['vis_soal'] = ambil_bagian("PERTANYAAN", txt)
            st.session_state['vis_kunci'] = ambil_bagian("JAWABAN", txt)
            st.session_state['vis_info'] = ambil_bagian("PENJELASAN", txt)
            st.session_state['vis_tipe'] = tipe
            st.session_state['gen_id'] = time.time()
            st.rerun() # Ditambahkan agar langsung muncul setelah klik
            
        except Exception as e:
            st.error(f"Kesalahan Generate: {e}")
# 5. TAMPILAN
if 'vis_soal' in st.session_state:
    st.divider()
    
    # Menampilkan Diagram
    st.subheader("🌐 Network Topology")
    st.code(st.session_state['vis_topologi'], language="text")
    
    # Menampilkan Soal
    st.subheader("📋 Pertanyaan")
    st.write(st.session_state['vis_soal'])
    
    # Tombol jawaban dengan KEY UNIK (menggunakan gen_id)
    key_tombol = f"btn_jawab_{st.session_state.get('gen_id', '0')}"
    
    if st.button("Tampilkan Jawaban & Solusi", key=key_tombol):
        st.success("✅ Kunci Jawaban / Langkah Konfigurasi:")
        if st.session_state.get('vis_tipe') == "Praktek / Lab":
            st.code(st.session_state['vis_kunci'], language="bash")
        else:
            st.write(st.session_state['vis_kunci'])
        st.info(f"**Penjelasan:**\n{st.session_state['vis_info']}")

    # Tombol reset dengan KEY UNIK
    if st.button("Hapus & Reset", key=f"reset_{st.session_state.get('gen_id', '0')}"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
