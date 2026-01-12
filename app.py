import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 1. CONFIGURAÇÃO (Tem de ser a primeira linha)
st.set_page_config(page_title="BIO-MAPA EXPERT", layout="wide")

# 2. ESTILO CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #adbac7; }
    .animal-card { 
        background-color: #1c2128; border-radius: 10px; padding: 15px; 
        border: 1px solid #444c56; margin-bottom: 10px;
    }
    img { border-radius: 8px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

# 3. DADOS DO MAPA (Formatados para não dar erro)
# Criamos latitudes e longitudes para Oceanos e Continentes
map_data = pd.DataFrame({
    'name': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 
             'Amazónia', 'Serengeti', 'Grande Barreira', 'Península Ibérica'],
    'lat': [0.0, 0.0, -20.0, 80.0, -3.46, -2.33, -18.28, 40.0],
    'lon': [-25.0, -160.0, 80.0, 0.0, -62.21, 34.83, 147.69, -3.7]
})

# 4. INTERFACE DO MAPA (Topo da página)
st.title("🌍 Bio-Mapa Interativo")

# Seletor para focar o mapa
escolha = st.selectbox("📍 Selecionar Região ou Oceano:", ["Explorar Global"] + list(map_data['name']))

# Definir o foco do mapa baseado na escolha
if escolha != "Explorar Global":
    foco = map_data[map_data['name'] == escolha].iloc[0]
    lat_ini, lon_ini, zoom_ini = foco['lat'], foco['lon'], 3
else:
    lat_ini, lon_ini, zoom_ini = 10.0, 0.0, 1

# --- O COMPONENTE DO MAPA ---
view_state = pdk.ViewState(
    latitude=lat_ini, 
    longitude=lon_ini, 
    zoom=zoom_ini, 
    pitch=0
)

# Camada de Círculos Verdes
layer = pdk.Layer(
    "ScatterplotLayer",
    map_data,
    get_position='[lon, lat]',
    get_color='[46, 160, 67, 200]', # Verde brilhante
    get_radius=800000,
    pickable=True,
)

# Renderizar o Mapa
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "{name}"}
))

st.markdown("---")

# 5. FERRAMENTAS (Abas)
tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "📝 FAVORITOS"])

with tab1:
    st.subheader("🧪 Pesquisa de Espécies")
    termo = st.text_input("Pesquisar no Laboratório:", value=escolha if escolha != "Explorar Global" else "")
    
    if termo and termo != "Explorar Global":
        # Chamada à API (Filtro Kingdom 1 = Animais)
        url = f"https://api.gbif.org/v1/species/search?q={termo}&kingdomKey=1&limit=9"
        try:
            res = requests.get(url).json().get('results', [])
            cols = st.columns(3)
            for i, animal in enumerate(res):
                if animal.get('kingdom') == 'Animalia':
                    with cols[i % 3]:
                        # Tenta buscar imagem no iNaturalist
                        nome_c = animal.get('canonicalName')
                        img_url = f"https://picsum.photos/seed/{animal.get('key')}/300/200"
                        try:
                            req_i = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome_c}&per_page=1").json()
                            if req_i['results']: img_url = req_i['results'][0]['default_photo']['medium_url']
                        except: pass
                        
                        st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{img_url}' width='100%'>
                            <h4 style='color:#2ea043;'>{nome_c}</h4>
                            <p style='font-size:12px;'><i>{animal.get('scientificName')}</i></p>
                        </div>
                        """, unsafe_allow_html=True)
        except:
            st.error("Erro ao carregar dados do Laboratório.")

with tab2:
    st.subheader("📅 Registo de Campo")
    c1, c2 = st.columns(2)
    c1.date_input("Data do Avistamento:")
    c2.text_input("Animal Avistado:")
    st.button("Guardar no Calendário")

with tab3:
    st.subheader("⭐ Favoritos e Notas")
    st.text_area("Notas científicas:", "Escreve aqui...")
