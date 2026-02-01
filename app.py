import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA (MundoVivo)
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E ANIMAÇÕES CANVA
st.markdown("""
    <style>
    /* Segurança: Esconder botões de sistema e gestão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* CARTÃO DE CIDADÃO */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 13px; margin-top: 8px;}
    .val-expert { color: white; font-size: 15px; margin-bottom: 4px; }

    /* CUTSCENE ANIMADA (ESTILO CANVA) */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 9999; display: flex; align-items: center; justify-content: center;
        animation: slideAway 2.5s forwards; pointer-events: none;
    }
    .forest-bg { background: linear-gradient(135deg, #062814 0%, #1c2128 100%); }
    .ocean-bg { background: linear-gradient(180deg, #001d3d 0%, #1c2128 100%); }

    @keyframes slideAway {
        0% { opacity: 1; transform: scale(1); }
        70% { opacity: 1; transform: scale(1.1); }
        100% { opacity: 0; transform: scale(1.2); visibility: hidden; }
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE DADOS
def definir_ambiente(classe, nome):
    n = str(nome).lower()
    if any(x in n for x in ['tubarão', 'peixe', 'orca', 'baleia', 'polvo', 'lula', 'coral']): return "Marinho / Aquático"
    if any(x in n for x in ['sapo', 'rã', 'jacaré', 'crocodilo', 'hipopótamo']): return "Ambiente Húmido"
    if any(x in n for x in ['camelo', 'dromedário', 'escorpião']): return "Árido / Deserto"
    return "Terrestre / Florestal"

def consultar_dieta_real(classe, nome):
    n = str(nome).lower()
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'serpente', 'tigre', 'jacaré', 'cobra']): return "Carnívoro (Predador)"
    if any(x in n for x in ['elefante', 'veado', 'vaca', 'zebra', 'girafa', 'coelho', 'canguru']): return "Herbívoro"
    return "Omnívoro / Variada"

def buscar_fauna(termo, lat=None, lon=None):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 24, "locale": "pt-BR"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 600})
    else: params.update({"q": termo})
    try:
        res = requests.get(url, params=params).json()
        lista = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                lista.append({
                    'nome': (t.get('preferred_common_name') or t.get('name')).title(),
                    'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url'],
                    'classe': t.get('iconic_taxon_name', 'Outros'),
                    'ambiente': definir_ambiente(t.get('iconic_taxon_name', ''), t.get('name')),
                    'dieta': consultar_dieta_real(t.get('iconic_taxon_name', ''), t.get('name')),
                    'repro': "Vivíparo" if 'mammalia' in t.get('iconic_taxon_name','').lower() else "Ovíparo"
                })
        return lista
    except: return []

# BASES DE DADOS (Países Solicitados)
paises_db = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'],
    'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41],
    'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]
})

florestas_db = pd.DataFrame({
    'nome': ['Amazónia', 'Congo', 'Taiga Siberiana', 'Bornéu', 'Floresta Negra'],
    'lat': [-3.46, -0.22, 61.52, 1.35, 48.0], 'lon': [-62.21, 23.61, 105.31, 113.8, 8.0]
})

oceanos_db = pd.DataFrame({
    'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico'],
    'lat': [0.0, -15.0, -20.0, 85.0], 'lon': [-25.0, -140.0, 70.0, 0.0]
})

# SESSÃO
if 'meus_favs_objetos' not in st.session_state: st.session_state.meus_favs_objetos = []
if 'diario' not in st.session_state: st.session_state.diario = ""

# SIDEBAR
st.sidebar.title("🌲 MundoVivo")
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

def desenhar_cartao(a, i, key_prefix):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{a['foto']}' class='img-cc'>
        <h3>{a['nome']}</h3>
        <div class='label-expert'>AMBIENTE NATURAL</div><div class='val-expert'>🏡 {a['ambiente']}</div>
        <div class='label-expert'>ALIMENTAÇÃO REAL</div><div class='val-expert'>🍴 {a['dieta']}</div>
        <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
        <div class='label-expert'>CIENTÍFICO</div><div class='val-expert'><i>{a['sci']}</i></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ Guardar", key=f"{key_prefix}_{i}"):
        if a not in st.session_state.meus_favs_objetos:
            st.session_state.meus_favs_objetos.append(a)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Global")
    st.map(paises_db, color='#2ea043')
    sel_p = st.selectbox("Escolha um País para ver os animais:", [""] + list(paises_db['nome']))
    if sel_p:
        sel = paises_db[paises_db['nome'] == sel_p].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "pla")

elif menu == "🌲 Florestas do Mundo":
    st.title("🌲 Exploração Florestal")
    st.map(florestas_db, color='#2ea043')
    f_sel = st.selectbox("Escolha a Floresta:", [""] + list(florestas_db['nome']))
    if f_sel:
        st.markdown("<div class='cutscene-overlay forest-bg'><h1>🌲 A entrar na floresta...</h1></div>", unsafe_allow_html=True)
        sel = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "for")

elif menu == "🌊 Oceanos":
    st.title("🌊 Todos os Oceanos")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Escolha o Oceano:", [""] + list(oceanos_db['nome']))
    if o_sel:
        st.markdown("<div class='cutscene-overlay ocean-bg'><h1>🌊 A mergulhar...</h1></div>", unsafe_allow_html=True)
        sel = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'])
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Espécies")
    p = st.text_input("Pesquisar animal:")
    if p:
        dados = buscar_fauna(p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário de Observação")
    st.session_state.diario = st.text_area("Notas sobre a vida selvagem:", value=st.session_state.diario, height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Os Meus Favoritos")
    if st.button("🗑️ Eliminar Todos"):
        st.session_state.meus_favs_objetos = []
        st.rerun()
    cols = st.columns(3)
    for i, a in enumerate(list(st.session_state.meus_favs_objetos)):
        with cols[i%3]:
            desenhar_cartao(a, i, "fav")
            if st.button(f"❌ Eliminar", key=f"del_{i}"):
                st.session_state.meus_favs_objetos.remove(a)
                st.rerun()
