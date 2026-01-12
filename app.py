import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="BIO-PORTAL 2026", layout="wide")

# Estilo Expert
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #adbac7; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1c2128; border-radius: 5px; padding: 10px; }
    .animal-card { background-color: #1c2128; border-radius: 10px; padding: 15px; border: 1px solid #444c56; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DADOS DO MAPA
# O st.map precisa obrigatoriamente de colunas chamadas 'lat' e 'lon'
locais_data = pd.DataFrame({
    'lat': [0.0, 0.0, -20.0, 80.0, -3.46, -2.33, -18.28, 40.0, -18.76, 35.0],
    'lon': [-25.0, -160.0, 80.0, 0.0, -62.21, 34.83, 147.69, -3.7, 46.86, 140.0],
    'regiao': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Amazónia', 'Serengeti', 'Grande Barreira', 'Península Ibérica', 'Madagáscar', 'Mar do Japão']
})

# 3. INTERFACE PRINCIPAL
st.title("🌍 BIO-COMMAND CENTER")

# MAPA NATIVO (Este é o que vai aparecer com 100% de certeza)
st.subheader("📍 Mapa Global de Biodiversidade")
st.map(locais_data, size=20, color='#2ea043') 

st.markdown("---")

# 4. FERRAMENTAS EM ABAS
escolha = st.selectbox("🎯 Focar Pesquisa numa Região:", ["Explorar Tudo"] + list(locais_data['regiao']))

tab1, tab2, tab3 = st.tabs(["🔬 LABORATÓRIO ANIMAL", "📅 CALENDÁRIO", "⭐ FAVORITOS"])

with tab1:
    st.header("🧪 Análise de Espécies")
    termo = st.text_input("Pesquisar animal ou região:", value=escolha if escolha != "Explorar Tudo" else "")
    
    if termo and termo != "Explorar Tudo":
        # Chamada à API Global
        url = f"https://api.gbif.org/v1/species/search?q={termo}&kingdomKey=1&limit=9"
        try:
            res = requests.get(url).json().get('results', [])
            cols = st.columns(3)
            for i, animal in enumerate(res):
                if animal.get('kingdom') == 'Animalia':
                    nome_c = animal.get('canonicalName', 'Desconhecido')
                    key = animal.get('key', i)
                    
                    # Sistema de Imagem Inteligente
                    img_url = f"https://picsum.photos/seed/{key}/300/200"
                    try:
                        req_i = requests.get(f"https://api.inaturalist.org/v1/taxa?q={nome_c}&per_page=1", timeout=1).json()
                        if req_i['results'] and req_i['results'][0].get('default_photo'):
                            img_url = req_i['results'][0]['default_photo']['medium_url']
                    except: pass
                    
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class='animal-card'>
                            <img src='{img_url}' style='width:100%; height:150px; object-fit:cover; border-radius:5px;'>
                            <h4 style='color:#2ea043;'>{nome_c}</h4>
                            <p style='font-size:12px; color:#8b949e;'>{animal.get('scientificName', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
        except:
            st.warning("A aguardar ligação às bases de dados zoofílicas...")

with tab2:
    st.header("📅 Diário de Observação")
    c1, c2 = st.columns(2)
    with c1:
        st.date_input("Data do Avistamento:")
        st.text_input("Espécie:")
    with c2:
        st.time_input("Hora:")
        st.button("Registar no Calendário")

with tab3:
    st.header("🌟 Favoritos e Notas")
    st.text_area("Bloco de Notas de Biólogo:", height=200, placeholder="Escreve aqui as tuas observações sobre os oceanos ou animais...")
