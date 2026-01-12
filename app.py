import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 1. CONFIGURAÇÃO EXPERT
st.set_page_config(page_title="BIO-EXPERT GLOBAL v2", layout="wide", page_icon="🐾")

# Estilo Dark Mode com toques de Ouro e Animal Print
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .animal-card { 
        border: 1px solid #ff9933; 
        border-radius: 15px; 
        padding: 15px; 
        background: #1c1e26;
        margin-bottom: 20px;
    }
    h1 { color: #ff9933; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE IMAGENS INTELIGENTE (Procura fotos reais)
def buscar_foto_expert(nome):
    # Tenta primeiro no iNaturalist (Base de dados de biólogos)
    try:
        url_inat = f"https://api.inaturalist.org/v1/taxa?q={nome}&per_page=1"
        res = requests.get(url_inat, timeout=3).json()
        if res['results']:
            foto = res['results'][0]['default_photo']['medium_url']
            return foto
    except:
        pass
    
    # Se falhar, tenta no Unsplash (Fotos Profissionais)
    try:
        url_un = f"https://source.unsplash.com/featured/?{nome},animal"
        return url_un
    except:
        return "https://images.unsplash.com/photo-1583337130417-3346a1be7dee"

# 3. BASE DE DADOS MUNDIAL (GBIF)
def obter_dados_expert(query):
    url = f"https://api.gbif.org/v1/species/search?q={query}&status=ACCEPTED&limit=15"
    try:
        return requests.get(url).json().get('results', [])
    except:
        return []

# 4. INTERFACE PRINCIPAL
st.markdown("<h1 style='text-align: center;'>🐆 BIO-EXPERT GLOBAL DATABASE 🐾</h1>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Módulos:", ["Globo de Biodiversidade", "Laboratório de Pesquisa", "Favoritos ❤️"])

# --- MÓDULO 1: GLOBO ---
if menu == "Globo de Biodiversidade":
    st.subheader("🌍 Mapa de Hotspots Biológicos")
    
    # Configuração do Globo Profissional
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1, pitch=45)
    
    layer = pdk.Layer(
        "ColumnLayer",
        data=pd.DataFrame({
            'lat': [48, 7, -15, 34, -25, -75, 40],
            'lon': [10, 21, -55, 100, 133, 0, -100],
            'value': [100, 200, 300, 150, 100, 50, 250]
        }),
        get_position='[lon, lat]',
        get_elevation='value',
        elevation_scale=10000,
        radius=200000,
        get_fill_color="[255, 153, 51, 140]",
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    regiao = st.selectbox("Explorar Fauna de:", ["Amazonas", "Serengeti", "Great Barrier Reef", "Arctico", "Iberia"])
    
    if regiao:
        with st.spinner("A consultar rede de biólogos..."):
            especies = obter_dados_expert(regiao)
            cols = st.columns(3)
            for idx, sp in enumerate(especies):
                with cols[idx % 3]:
                    nome_comum = sp.get('canonicalName', 'Desconhecido')
                    st.markdown(f"""<div class='animal-card'>
                        <img src='{buscar_foto_expert(nome_comum)}' style='width:100%; border-radius:10px;'>
                        <h3 style='color:#ff9933;'>{nome_comum}</h3>
                        <p style='font-style:italic; font-size:12px;'>{sp.get('scientificName', '')}</p>
                        <p style='font-size:11px;'>Classe: {sp.get('class', 'N/A')}</p>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Guardar {nome_comum}", key=f"btn_{idx}"):
                        st.session_state.setdefault('favs', []).append(nome_comum)

# --- MÓDULO 2: PESQUISA ---
elif menu == "Laboratório de Pesquisa":
    st.subheader("🔍 Filtro Taxonómico de Alta Precisão")
    query = st.text_input("Insira Nome Científico ou Comum:")
    
    if query:
        dados = obter_dados_expert(query)
        for d in dados:
            c1, c2 = st.columns([1, 2])
            nome = d.get('canonicalName', 'N/A')
            c1.image(buscar_foto_expert(nome))
            c2.write(f"### {nome}")
            c2.write(f"**Reino:** {d.get('kingdom', 'N/A')} | **Família:** {d.get('family', 'N/A')}")
            c2.info(f"Status: {d.get('taxonomicStatus', 'N/A')}")
            st.divider()

# --- MÓDULO 3: FAVORITOS ---
else:
    st.subheader("❤️ Espécies Marcadas")
    if 'favs' in st.session_state:
        for f in set(st.session_state['favs']):
            st.write(f"⭐ {f}")
    else:
        st.write("Lista vazia.")
