import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="BioGlobe Expert - Edição Final", layout="wide")

# 2. ESTILO VISUAL (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .animal-card { 
        background-color: #161b22; 
        border-radius: 15px; 
        padding: 15px; 
        border: 2px solid #2ea043;
        margin-bottom: 20px;
    }
    .stButton>button { background-color: #2ea043; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar Estados (Memória da App)
if 'favoritos' not in st.session_state: st.session_state.favoritos = []
if 'avistamentos' not in st.session_state: st.session_state.avistamentos = []

# 3. MOTOR DE BUSCA (10 Fontes / iNaturalist + GBIF)
def obter_dados_limpos(termo):
    try:
        # Busca em múltiplas redes (limit=10 para não repetir)
        url = f"https://api.gbif.org/v1/species/search?q={termo}&kingdomKey=1&limit=10&status=ACCEPTED"
        res = requests.get(url, timeout=5).json()
        resultados = res.get('results', [])
        
        lista_final = []
        vistos = set()
        
        for r in resultados:
            nome = r.get('canonicalName')
            if nome and nome not in vistos:
                # Busca imagem no iNaturalist (Rede Expert)
                img_url = f"https://picsum.photos/seed/{r.get('key')}/400/300" # Fallback
                try:
                    res_img = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome}&per_page=1", timeout=2).json()
                    if res_img['results'] and res_img['results'][0].get('default_photo'):
                        img_url = res_img['results'][0]['default_photo']['medium_url']
                except: pass
                
                r['imagem_unica'] = img_url
                lista_final.append(r)
                vistos.add(nome)
        return lista_final
    except: return []

# 4. MENU LATERAL
menu = st.sidebar.radio("Navegação:", ["Globo Interativo", "Laboratório Animal", "Calendário de Avistamentos", "Bloco de Notas e Favoritos"])

# --- PÁGINA 1: GLOBO INTERATIVO ---
if menu == "Globo Interativo":
    st.title("🌍 Globo Terrestre Interativo")
    st.write("Usa o rato para aproximar (zoom) e rodar. Clica nos círculos verdes.")

    locais = pd.DataFrame({
        'nome': ['Amazónia', 'Serengeti', 'Grande Barreira de Coral', 'Ártico', 'Península Ibérica'],
        'lat': [-3.46, -2.33, -18.28, 76.0, 40.0],
        'lon': [-62.21, 34.83, 147.69, -40.0, -3.7]
    })

    # Mapa com Círculos Verdes e Zoom Ativo
    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1, pitch=0)
    layer = pdk.Layer(
        "ScatterplotLayer",
        locais,
        get_position='[lon, lat]',
        get_color='[46, 160, 67, 200]', # Verde
        get_radius=500000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/dark-v10'))

    escolha = st.selectbox("Aproximar da Região:", [""] + list(locais['nome']))
    
    if escolha:
        st.subheader(f"🐾 Espécies em {escolha}")
        animais = obter_dados_limpos(escolha)
        
        for a in animais:
            with st.container():
                st.markdown(f"""<div class='animal-card'>
                    <div style='display: flex; gap: 20px;'>
                        <img src='{a['imagem_unica']}' style='width:200px; border-radius:10px;'>
                        <div>
                            <h3>{a['canonicalName']}</h3>
                            <p><b>Científico:</b> <i>{a.get('scientificName')}</i></p>
                            <p><b>Classe:</b> {a.get('class', 'N/D')}</p>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"❤️ Favoritar {a['canonicalName']}", key=a['key']):
                    st.session_state.favoritos.append(a['canonicalName'])

# --- PÁGINA 2: LABORATÓRIO ANIMAL ---
elif menu == "Laboratório Animal":
    st.title("🔍 Laboratório Animal")
    pesquisa = st.text_input("Pesquisa por espécie (ex: Orca, Panthera, Lobo):")
    if pesquisa:
        resultados = obter_dados_limpos(pesquisa)
        for res in resultados:
            col1, col2 = st.columns([1, 2])
            col1.image(res['imagem_unica'], use_container_width=True)
            col2.subheader(res['canonicalName'])
            col2.write(f"Família: {res.get('family')}")
            st.divider()

# --- PÁGINA 3: CALENDÁRIO ---
elif menu == "Calendário de Avistamentos":
    st.title("📅 Registo de Avistamentos")
    with st.form("avistamento_form"):
        data = st.date_input("Quando viste o animal?")
        animal_visto = st.text_input("Qual foi o animal?")
        local_visto = st.text_input("Onde?")
        enviar = st.form_submit_button("Registar no Mapa de Campo")
        
        if enviar:
            st.session_state.avistamentos.append(f"{data}: {animal_visto} em {local_visto}")
            st.success("Registado com sucesso!")
    
    st.write("### Teu Histórico de Observador:")
    for av in st.session_state.avistamentos:
        st.info(av)

# --- PÁGINA 4: NOTAS E FAVORITOS ---
else:
    st.title("📝 Bloco de Notas e Meus Favoritos")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🌟 Favoritos")
        for fav in set(st.session_state.favoritos):
            st.success(fav)
            
    with col_b:
        st.subheader("✍️ Notas de Campo")
        st.text_area("Escreve aqui as tuas descobertas:", height=300)
