def buscar_muitos_animais(lat, lon):
    # Adicionámos '&locale=pt-BR' para forçar a tradução da base de dados
    url = f"https://api.inaturalist.org/v1/observations?lat={lat}&lng={lon}&radius=500&taxon_id=1&per_page=30&order=desc&order_by=votes&locale=pt-BR"
    
    try:
        res = requests.get(url, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            taxon = obs.get('taxon')
            if taxon:
                # A API do iNaturalist já tenta traduzir se o locale estiver ativo
                nome_pt = taxon.get('preferred_common_name')
                
                if not nome_pt:
                    nome_pt = taxon.get('name') # Nome científico se não houver comum
                
                if nome_pt not in vistos and taxon.get('default_photo'):
                    lista.append({
                        'nome': nome_pt,
                        'sci': taxon.get('name'),
                        'foto': taxon['default_photo']['medium_url']
                    })
                    vistos.add(nome_pt)
        return lista
    except: return []import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="BIO-MAPA 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .animal-card { 
        background: #161b22; border-radius: 10px; padding: 10px; 
        border: 1px solid #2ea043; text-align: center; height: 320px;
    }
    .img-zoom { width: 100%; height: 180px; object-fit: cover; border-radius: 5px; }
    h3 { font-size: 16px !important; color: #2ea043; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DADOS AMPLIADA
locais = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Amazónia', 'Serengeti', 'Austrália', 'Portugal', 'Antártida', 'Arquipélago Galápagos'],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5, -75.25, -0.95],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0, 0.0, -90.96]
})

# 3. MOTOR DE BUSCA POR COORDENADAS (Traz muito mais animais)
def buscar_muitos_animais(lat, lon):
    # Pesquisa num raio de 500km das coordenadas escolhidas
    url = f"https://api.inaturalist.org/v1/observations?lat={lat}&lng={lon}&radius=500&taxon_id=1&per_page=30&order=desc&order_by=votes"
    try:
        res = requests.get(url, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            taxon = obs.get('taxon')
            if taxon:
                nome = taxon.get('preferred_common_name') or taxon.get('name')
                if nome not in vistos and taxon.get('default_photo'):
                    lista.append({
                        'nome': nome,
                        'sci': taxon.get('name'),
                        'foto': taxon['default_photo']['medium_url']
                    })
                    vistos.add(nome)
        return lista
    except: return []

# 4. INTERFACE: MAPA E COMANDO
st.title("🌍 BIO-COMMAND CENTER v3.0")

st.subheader("📍 Seleciona a Região no Mapa")
col_map, col_ctrl = st.columns([2, 1])

with col_ctrl:
    escolha = st.selectbox("Escolha o Hotspot:", [""] + list(locais['nome']))
    if escolha:
        sel = locais[locais['nome'] == escolha].iloc[0]
        lat_f, lon_f = sel['lat'], sel['lon']
    else:
        lat_f, lon_f = 20, 0

with col_map:
    # Mostra o mapa com círculos
    st.map(locais, size=40, color='#2ea043')

st.divider()

# 5. RESULTADOS E FERRAMENTAS
if escolha:
    # Sincronização automática: Quando escolhes no menu, ele pesquisa por coordenadas
    tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL (30+ ESPÉCIES)", "📅 CALENDÁRIO", "⭐ FAVORITOS"])
    
    with tab1:
        st.header(f"🔎 Explorando a Biodiversidade de {escolha}")
        animais = buscar_muitos_animais(lat_f, lon_f)
        
        if animais:
            # Organiza em 4 colunas para caberem mais animais no ecrã
            cols = st.columns(4)
            for idx, a in enumerate(animais):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class='animal-card'>
                        <img src='{a['foto']}' class='img-zoom'>
                        <h3>{a['nome'].title()}</h3>
                        <p style='font-size:11px; color:#888;'><i>{a['sci']}</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"❤️ Guardar", key=f"f_{idx}"):
                        if 'favs' not in st.session_state: st.session_state.favs = []
                        st.session_state.favs.append(a['nome'])
        else:
            st.error("Erro de conexão. Tenta selecionar a região novamente.")

    with tab2:
        st.subheader("📅 Registo de Observação")
        # Formulário simples
        st.date_input("Data:")
        st.text_input("Animal visto:")
        st.button("Registar")

    with tab3:
        st.subheader("⭐ Os Teus Favoritos")
        for f in set(st.session_state.get('favs', [])):
            st.success(f"🐾 {f}")
else:
    st.info("💡 Seleciona uma região no menu lateral do mapa para carregar a lista completa de animais.")

