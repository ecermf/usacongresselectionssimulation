import streamlit as st
import numpy as np

# Sayfa Yapılandırması
st.set_page_config(page_title="Meclis Strateji Sim - Master", layout="wide")
st.title("🏛️ ABD Meclis: Kapsamlı Eyalet ve Politika Simülatörü")

# 1. STRATEJİK SENARYO MATRİSİ
yasalar = {
    "Teknoloji ve İnovasyon Teşviki (CA)": {
        "sektor": "Teknoloji", "eyalet": "Kaliforniya", "sponsor": "Cumhuriyetçiler",
        "e_rep": 12, "e_dem": 40, "toplam": 52
    },
    "Finansal Altyapı ve Bankacılık (NY)": {
        "sektor": "Finans", "eyalet": "New York", "sponsor": "Cumhuriyetçiler",
        "e_rep": 11, "e_dem": 15, "toplam": 26
    },
    "Ulaşım ve Lojistik Modernizasyonu (IL)": {
        "sektor": "Lojistik", "eyalet": "Illinois", "sponsor": "Cumhuriyetçiler",
        "e_rep": 3, "e_dem": 14, "toplam": 17
    },
    "Enerji Bağımsızlığı ve Sondaj (TX)": {
        "sektor": "Petrol & Gaz", "eyalet": "Teksas", "sponsor": "Demokratlar",
        "e_rep": 25, "e_dem": 13, "toplam": 38
    },
    "Havacılık ve Uzay Yatırım Fonu (FL)": {
        "sektor": "Savunma", "eyalet": "Florida", "sponsor": "Demokratlar",
        "e_rep": 20, "e_dem": 8, "toplam": 28
    },
    "Üretim ve Sanayi Teşvik Yasası (OH)": {
        "sektor": "İmalat", "eyalet": "Ohio", "sponsor": "Cumhuriyetçiler",
        "e_rep": 10, "e_dem": 5, "toplam": 15
    },
    "Tarım ve Kırsal Kalkınma Fonu (NC)": {
        "sektor": "Tarım", "eyalet": "North Carolina", "sponsor": "Cumhuriyetçiler",
        "e_rep": 7, "e_dem": 7, "toplam": 14
    }
}

# 2. YAN MENÜ
st.sidebar.header("📋 Senaryo Ayarları")
secilen_yasa_adi = st.sidebar.selectbox("Bir Yasa Tasarısı Seçin", list(yasalar.keys()))
yasa = yasalar[secilen_yasa_adi]

st.sidebar.divider()
st.sidebar.subheader("👥 Meclis Aritmetiği")
rep_seats = st.sidebar.slider("Toplam Cumhuriyetçi (R)", 0, 435, 218)
dem_seats = 435 - rep_seats
st.sidebar.info(f"🔵 Toplam Demokrat (D): {dem_seats}")

st.sidebar.divider()
st.sidebar.subheader("📢 Lobi ve Kamuoyu")
lobi_destek = st.sidebar.slider("Destekçi Lobi (Evet)", 0, 100, 50)
lobi_karsi = st.sidebar.slider("Muhalif Lobi (Hayır)", 0, 100, 50)

# YENİ EKLENEN BÖLÜM: Makro ve Politik Kriz Durumları
st.sidebar.divider()
st.sidebar.subheader("🌍 Makro ve Politik Kriz Durumları")
mevcut_hukumet = st.sidebar.radio("Mevcut Hükümet (Başkan):", ["Cumhuriyetçiler", "Demokratlar"])
savas_durumu = st.sidebar.checkbox("Savaş Durumu (Ulusal Birlik Etkisi)")
yuksek_enflasyon = st.sidebar.checkbox("Enflasyon > %5 (Ekonomik Baskı)")
skandal_medya = st.sidebar.checkbox("Skandal / Ağır Medya Baskısı")

# 3. HESAPLAMA MOTORU
def analiz_et():
    n = 10000 
    net_lobi = (lobi_destek - lobi_karsi) / 100
    e_total, e_rep, e_dem = yasa['toplam'], yasa['e_rep'], yasa['e_dem']
    
    if yasa['sponsor'] == "Cumhuriyetçiler":
        rep_base, dem_base = 0.92, 0.08
    else:
        rep_base, dem_base = 0.08, 0.92

    # YENİ EKLENEN BÖLÜM: Kriz Mantığı Hesaplamaları
    hukumet_sponsor_mu = (yasa['sponsor'] == mevcut_hukumet)

    if savas_durumu:
        if yasa['sponsor'] == "Cumhuriyetçiler":
            dem_base += 0.15
        else:
            rep_base += 0.15

    if yuksek_enflasyon:
        if hukumet_sponsor_mu:
            if yasa['sponsor'] == "Cumhuriyetçiler":
                rep_base -= 0.10
                dem_base -= 0.05
            else:
                dem_base -= 0.10
                rep_base -= 0.05

    if skandal_medya:
        rep_base -= 0.20
        dem_base -= 0.20
        net_lobi = net_lobi * 0.3 

    rep_base = max(0.0, min(1.0, rep_base))
    dem_base = max(0.0, min(1.0, dem_base))
    # EKLENEN BÖLÜMÜN SONU

    p_eyalet = np.clip(0.60 + (net_lobi * 0.35), 0.05, 0.95)
    kalan_rep = max(0, rep_seats - e_rep)
    kalan_dem = max(0, dem_seats - e_dem)
    noise = np.random.normal(0, 0.03, n)
    
    eyalet_votes = np.random.binomial(e_total, p_eyalet, n)
    rep_votes = np.random.binomial(kalan_rep, np.clip(rep_base + (net_lobi/7) + noise, 0.01, 0.99), n)
    dem_votes = np.random.binomial(kalan_dem, np.clip(dem_base + (net_lobi/7) + noise, 0.01, 0.99), n)
    
    toplam_evet = eyalet_votes + rep_votes + dem_votes
    return (np.sum(toplam_evet >= 218) / n) * 100, np.mean(toplam_evet), p_eyalet

# 4. GÖRSEL ARAYÜZ
st.subheader(f"📄 {secilen_yasa_adi}")

st.markdown(f"""
**Yasa Sponsoru:** {yasa['sponsor']}  
**Odak Eyalet:** {yasa['eyalet']}  
**Eyalet Delegasyon Yapısı:** Toplam {yasa['toplam']} Vekil (**{yasa['e_rep']} Cumhuriyetçi / {yasa['e_dem']} Demokrat**)
""")

if st.button("📊 ANALİZİ BAŞLAT", use_container_width=True):
    oran, ort_oy, p_e = analiz_et()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Geçme Olasılığı", f"%{oran:.1f}")
    c2.metric("Tahmini 'EVET' Oyu", f"{int(ort_oy)} / 435")
    c3.metric(f"{yasa['eyalet']} Eğilimi", f"%{p_e*100:.0f} Evet")

    st.divider()
    st.write("### 📝 Stratejik Notlar")
    
    col_x, col_y = st.columns(2)
    with col_x:
        is_paradox = (yasa['sponsor'] == "Cumhuriyetçiler" and yasa['e_dem'] > yasa['e_rep']) or \
                     (yasa['sponsor'] == "Demokratlar" and yasa['e_rep'] > yasa['e_dem'])
        
        if is_paradox:
            st.info(f"**Politik Paradoks:** Sponsor parti ile eyalet çoğunluğu zıt. Eyaletteki {max(yasa['e_rep'], yasa['e_dem'])} muhalif vekilin yerel çıkar için saf değiştirme ihtimali inceleniyor.")
        else:
            st.success(f"**Siyasi Sinerji:** Sponsor parti ve eyalet yapısı uyumlu. {yasa['eyalet']} delegasyonu yasaya doğal destek eğiliminde.")
    
    with col_y:
        if oran > 60:
            st.success(f"✅ **Piyasa Yorumu:** {yasa['sektor']} sektörü için ralli beklentisi.")
        elif oran < 40:
            st.error(f"❌ **Piyasa Yorumu:** Siyasi direnç aşılamıyor.")
        else:
            st.warning("⚠️ **Piyasa Yorumu:** Bıçak sırtı oylama.")