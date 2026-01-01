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

# 4. LOGIKA GENERATE
if generate_btn and topik:
    with st.spinner("AI sedang merancang soal dan topologi..."):
        # Kita minta AI menggunakan penanda yang lebih kaku agar split tidak gagal
        prompt = f"""
        Buatkan 1 soal {tipe} tentang {topik}.
        Gunakan format pemisah [BAGIAN] agar sistem tidak error.
        
        [TOPOLOGI]
        (Buat diagram ASCII jaringan)
        
        [PERTANYAAN]
        (Isi soal atau skenario)
        
        [JAWABAN]
        (Isi kunci jawaban atau CLI)
        
        [PENJELASAN]
        (Isi penjelasan singkat)
        """
        
        try:
            response = model.generate_content(prompt)
            txt = response.text
            
            # Fungsi potong teks yang lebih aman
            def ambil_bagian(tag, teks):
                try:
                    return teks.split(f"[{tag}]")[1].split("[")[0].strip()
                except:
                    return f"Bagian {tag} tidak tergenerasi dengan sempurna."

            st.session_state['vis_topologi'] = ambil_bagian("TOPOLOGI", txt)
            st.session_state['vis_soal'] = ambil_bagian("PERTANYAAN", txt)
            st.session_state['vis_kunci'] = ambil_bagian("JAWABAN", txt)
            st.session_state['vis_info'] = ambil_bagian("PENJELASAN", txt)
            st.session_state['vis_tipe'] = tipe
            # Gunakan timestamp agar ID selalu unik setelah generate
            st.session_state['gen_id'] = time.time() 
            
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
