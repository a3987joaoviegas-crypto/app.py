import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# Estilo visual dos Cartões
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 14px; margin-bottom: 2px; }
    .val-expert { color: white; font-size: 16px; margin-bottom: 10px; }
    h1, h2, h3 { color: #2ea043 !important; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE ALIMENTAÇÃO REALISTA
def consultar_dieta_real(classe, nome):
    n = str(nome).lower()
    c = str(classe).lower()
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'falcão', 'orca', 'serpente', 'tigre', 'jacaré', 'raposa', 'gavião', 'polvo', 'coruja', 'sapo', 'rã', 'lagarto', 'aranha', 'foca', 'pinguim', 'crocodilo', 'lince', 'leopardo', 'garça', 'pelicano', 'fuinha', 'doninha', 'mocho', 'cobra']):
        return "Carnívoro (Predador)"
    if any(x in n for x in ['elefante', 'veado', 'corça', 'vaca', 'zebra', 'girafa', 'coelho', 'cavalo', 'ovelha', 'cabra', 'hipopótamo', 'rinoceronte', 'canguru', 'coala', 'panda', 'tartaruga', 'papagaio', 'beija-flor', 'gazela', 'búfalo', 'capivara', 'borboleta', 'abelha', 'grilo', 'gafanhoto', 'veada', 'coelha', 'lebre']):
        return "Herbívoro (Plantas/Frutos)"
    if any(x in n for x in ['porco', 'javali', 'urso', 'macaco', 'chimpanzé', 'rato', 'galinha', 'corvo', 'guaxinim', 'esquilo', 'humano', 'suricata', 'formiga', 'texugo', 'avestruz', 'pombo']):
        return "Omnívoro"
    if 'reptilia' in c or 'amphibia' in c: return "Carnívoro / Insetívoro"
    if 'arachnida' in c: return "Carnívoro"
    if 'actinopterygii' in c: return "Piscívoro (Carnívoro)"
    return "Dieta Variada / Omnívoro"

def definir_repro(classe):
    return "Vivíparo" if 'mammalia' in str(classe).lower() else "Ovíparo"

# MOTOR DE BUSCA
def buscar_fauna(termo, lat=None, lon=None):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 70, "locale": "pt-BR", "order": "desc", "order_by": "votes"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 600})
    else: params.update({"q": termo})
    try:
        res = requests.get(url, params=params, timeout=10).json()
        lista = []
        vistos = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                nome = t.get('preferred_common_name') or t.get('name')
                if nome not in vistos:
                    lista.append({
                        'nome': nome.title(),
                        'sci': t.get('name'),
                        'foto': t['default_photo']['medium_url'],
                        'classe': t.get('iconic_taxon_name', 'Outros'),
                        'repro': definir_repro(t.get('iconic_taxon_name', '')),
                        'dieta': consultar_dieta_real(t.get('iconic_taxon_name', ''), nome)
                    })
                    vistos.add(nome)
        return lista
    except: return []

# BASE DE DADOS (21 regiões)
locais = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Amazónia', 'Serengeti', 'Austrália', 'Portugal', 'Península de Yucatán', 'Rússia', 'Madagascar', 'Ilhas Maurícias', 'Havai', 'Israel', 'Ilhas Fiji', 'Maldivas', 'México', 'Argentina', 'Finlândia', 'Moldávia', 'Polónia'],
    'lat': [0.0, -15.0, -20.0, 85.0, -3.46, -2.33, -25.27, 39.5, 18.84, 61.52, -18.76, -20.34, 21.31, 31.05, -17.71, 3.20, 23.63, -38.41, 61.92, 47.41, 51.91],
    'lon': [-25.0, -140.0, 70.0, 0.0, -62.21, 34.83, 133.77, -8.0, -89.11, 105.31, 46.86, 57.55, -157.86, 34.85, 178.07, 73.22, -102.55, -63.61, 25.74, 28.36, 19.14]
})

# FLORESTAS DO MUNDO
florestas_db = pd.DataFrame({
    'nome': ['Floresta Amazónica', 'Floresta do Congo', 'Taiga Siberiana', 'Floresta Nacional de Tongass', 'Daintree Rainforest', 'Selva de Bornéu', 'Floresta Negra'],
    'lat': [-3.46, -0.22, 61.52, 57.17, -16.17, 1.35, 48.0],
    'lon': [-62.21, 23.61, 105.31, -134.58, 145.41, 113.8, 8.0]
})

# OCEANOS DO MUNDO
oceanos_db = locais[locais['nome'].str.contains('Oceano')]

# GESTÃO DE FAVORITOS
if 'meus_favs_objetos' not in st.session_state:
    st.session_state.meus_favs_objetos = []

# NAVEGADOR
st.sidebar.title("📑 Navegador")
menu = st.sidebar.radio("Ir para:", [
    "🌍 Planisfério e Animais", 
    "🌲 Florestas do Mundo", 
    "🌊 Todos os Oceanos", 
    "🔬 Laboratório Global", 
    "📝 Bloco de Notas", 
    "⭐ Favoritos"
])

def desenhar_cartao(animal):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{animal['foto']}' class='img-cc'>
        <h3>{animal['nome']}</h3>
        <div class='label-expert'>NOME CIENTÍFICO</div>
        <div class='val-expert'><i>{animal['sci']}</i></div>
        <div class='label-expert'>MÉTODO REPRODUTIVO</div>
        <div class='val-expert'>🧬 {animal['repro']}</div>
        <div class='label-expert'>ALIMENTAÇÃO REAL</div>
        <div class='val-expert'>🍴 {animal['dieta']}</div>
        <div class='label-expert'>CLASSE BIOLÓGICA</div>
        <div class='val-expert'>🏷️ {animal['classe']}</div>
    </div>
    """, unsafe_allow_html=True)

# INTERFACES
if menu == "🌍 Planisfério e Animais":
    st.title("🌍 EXPLORAÇÃO POR REGIÃO E CLASSE")
    st.map(locais, color='#2ea043')
    col1, col2 = st.columns(2)
    with col1:
        regiao = st.selectbox("📍 1. Escolha o País/Região:", [""] + list(locais['nome']))
    with col2:
        classe_filtro = st.selectbox("🐾 2. Filtrar por Classe:", ["Todas", "Mammalia", "Aves", "Reptilia", "Amphibia", "Actinopterygii", "Insecta"])
    if regiao:
        sel = locais[locais['nome'] == regiao].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        if classe_filtro != "Todas": dados = [a for a in dados if a['classe'] == classe_filtro]
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                desenhar_cartao(a)
                if st.button(f"⭐ Guardar Favorito", key=f"reg_{i}"):
                    if a not in st.session_state.meus_favs_objetos: st.session_state.meus_favs_objetos.append(a)

elif menu == "🌲 Florestas do Mundo":
    # CUTSCENE FLORESTA
    st.video("https://assets.mixkit.co/videos/preview/mixkit-walking-through-a-dense-green-forest-4286-large.mp4", format="video/mp4", start_time=0)
    time.sleep(1) # Simula o tempo da cutscene
    st.title("🌲 Grandes Florestas do Mundo")
    st.map(florestas_db, color='#2ea043')
    f_escolha = st.selectbox("Escolha uma Floresta para explorar:", [""] + list(florestas_db['nome']))
    if f_escolha:
        sel = florestas_db[florestas_db['nome'] == f_escolha].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                desenhar_cartao(a)
                if st.button(f"⭐ Guardar", key=f"for_{i}"): st.session_state.meus_favs_objetos.append(a)

elif menu == "🌊 Todos os Oceanos":
    # CUTSCENE BOLHAS/OCEANO
    st.video("https://assets.mixkit.co/videos/preview/mixkit-bubbles-rising-to-the-surface-of-the-ocean-34753-large.mp4", format="video/mp4")
    time.sleep(1)
    st.title("🌊 Vida Marinha nos Oceanos")
    st.map(oceanos_db, color='#0077be')
    o_escolha = st.selectbox("Escolha um Oceano:", [""] + list(oceanos_db['nome']))
    if o_escolha:
        sel = oceanos_db[oceanos_db['nome'] == o_escolha].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                desenhar_cartao(a)
                if st.button(f"⭐ Guardar", key=f"oce_{i}"): st.session_state.meus_favs_objetos.append(a)

elif menu == "🔬 Laboratório Global":
    st.title("🔬 Pesquisa Livre")
    pesq = st.text_input("Procurar animal:")
    if pesq:
        dados = buscar_fauna(pesq)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]:
                desenhar_cartao(a)
                if st.button(f"⭐ Guardar Favorito", key=f"lab_{i}"):
                    if a not in st.session_state.meus_favs_objetos: st.session_state.meus_favs_objetos.append(a)

elif menu == "📝 Bloco de Notas":
    st.title("📝 Notas")
    st.session_state.notas = st.text_area("Escreve aqui:", value=st.session_state.get('notas', ''), height=300)

elif menu == "⭐ Favoritos":
    st.title("⭐ Os Meus Favoritos")
    if st.session_state.meus_favs_objetos:
        if st.button("🗑️ Eliminar Todos os Favoritos"):
            st.session_state.meus_favs_objetos = []
            st.rerun()
        st.markdown("---")
        cols = st.columns(3)
        for i, a in enumerate(list(st.session_state.meus_favs_objetos)):
            with cols[i%3]:
                desenhar_cartao(a)
                if st.button(f"❌ Eliminar Animal", key=f"del_{i}"):
                    st.session_state.meus_favs_objetos.remove(a)
                    st.rerun()
    else:
        st.info("A tua lista de favoritos está vazia.")
