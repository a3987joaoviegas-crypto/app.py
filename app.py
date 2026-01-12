import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from datetime import datetime

# 1. CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="BIO-COMMAND CENTER", layout="wide", page_icon="🌍")

# Estilo Pro-Sleek (Dark Mode com acentos verdes e organização em blocos)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #adbac7; }
    .main-header { text-align: center; color: #2ea043; text-shadow: 0 0 15px rgba(46,160,67,0.4); }
    .section-box { 
        background-color: #1c2128; border-radius: 10px; padding: 20px; 
        border: 1px solid #444c56; margin-top: 20px;
    }
    .animal-card {
        background: #22272e; border-radius: 8px; padding: 15px;
        border-bottom: 3px solid #2ea043; transition: 0.3s;
    }
    .animal-card:hover { background: #2d333b; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE BUSCA (Filtro Estrito: Apenas Animais)
def fetch_animal_data(query):
    try:
        url = f"https://api.gbif.org/v1/species/search?q={query}&kingdomKey=1&limit=12&status=ACCEPTED"
        data = requests.get(url, timeout=5).json().get('results', [])
        final_list = []
        seen = set()
        for item in data:
            name = item.get('canonicalName')
            if name and name not in seen and item.get('kingdom') == 'Animalia':
                # Imagem inteligente
                img = f"https://picsum.photos/seed/{item.get('key')}/400/300"
                try:
                    res_img = requests.get(f"https://api.inaturalist.org/v1/taxa?q={name}&per_page=1", timeout=2).json()
                    if res_img['results']: img = res_img['results'][0]['default_photo']['medium_url']
                except: pass
                item['thumb'] = img
                final_list.append(item)
                seen.add(name)
        return final_list
    except: return []

# 3. CABEÇALHO E GLOBO (Sempre no Topo)
st.markdown("<h1 class='main-header'>🌍 BIO-COMMAND CENTER: GLOBAL FAUNA</h1>", unsafe_allow_html=True)

# Dados de Regiões e Oceanos
locations = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Amazónia', 'Serengeti', 'Grande Barreira', 'Península Ibérica'],
    'lat': [0.0, 0.0, -20.0, 80.0, -3.46, -2.33, -18.28, 40.0],
    'lon': [-25.0, -160.0, 80.0, 0.0, -62.21, 34.83, 147.69, -3.7]
})

col_nav, col_map = st.columns([1, 2])

with col_nav:
    st.markdown("### 📡 Radar de Região")
    selection = st.selectbox("Focar em:", ["Global"] + list(locations['nome']))
    if selection != "Global":
        row = locations[locations['nome'] == selection].iloc[0]
        lat, lon, zoom = row['lat'], row['lon'], 3
    else:
        lat, lon, zoom = 15, 0, 1

with col_map:
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom, pitch=40)
    layer = pdk.Layer(
        "ScatterplotLayer", locations, get_position='[lon, lat]',
        get_color='[46, 160, 67, 200]', get_radius=700000, pickable=True
    )
    st.pydeck_chart(pdk.Deck(
        layers=[layer], initial_view_state=view_state, 
        map_style='mapbox://styles/mapbox/dark-v10',
        tooltip={"text": "{nome}"}
    ))

st.markdown("---")

# 4. FERRAMENTAS (Laboratório, Calendário e Favoritos em Abas)
tab_lab, tab_cal, tab_notes = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO DE CAMPO", "📝 NOTAS & FAVORITOS"])

with tab_lab:
    st.subheader("🧪 Análise de Espécies")
    search_query = st.text_input("Pesquisar no Laboratório (Nome comum ou científico):", 
                                value=selection if selection != "Global" else "")
    
    if search_query:
        with st.spinner(f"A analisar DNA digital de {search_query}..."):
            results = fetch_animal_data(search_query)
            if results:
                cols = st.columns(3)
                for idx, animal in enumerate(results):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{animal['thumb']}' style='width:100%; height:150px; object-fit:cover; border-radius:5px;'>
                            <h4 style='color:#2ea043;'>{animal['canonicalName']}</h4>
                            <p style='font-size:11px;'><i>{animal.get('scientificName')}</i></p>
                            <p style='font-size:10px; color:#8b949e;'>Classe: {animal.get('class', 'N/D')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"⭐ Fav {idx}", key=f"fav_{animal['key']}"):
                            st.session_state.setdefault('my_favs', []).append(animal['canonicalName'])
            else:
                st.warning("Nenhum animal encontrado. Tenta outro termo!")

with tab_cal:
    st.subheader("📅 Registo de Avistamentos")
    c1, c2 = st.columns(2)
    with c1:
        date_obs = st.date_input("Data:")
        animal_obs = st.text_input("Espécie observada:")
    with c2:
        local_obs = st.text_input("Localização:")
        if st.button("Guardar no Diário"):
            st.session_state.setdefault('history', []).append(f"✅ {date_obs} | {animal_obs} ({local_obs})")
    
    st.markdown("#### Histórico Recente")
    for item in reversed(st.session_state.get('history', [])):
        st.info(item)

with tab_notes:
    col_f, col_n = st.columns(2)
    with col_f:
        st.subheader("🌟 Favoritos")
        for f in set(st.session_state.get('my_favs', [])):
            st.write(f"🐾 {f}")
    with col_n:
        st.subheader("✍️ Bloco de Notas Científico")
        st.text_area("Insira as suas conclusões:", height=200)
