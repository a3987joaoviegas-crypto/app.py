import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E CUTSCENE APROVADA
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 20px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 12px; margin-top: 5px;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 8px; }

    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 9999; display: flex; align-items: center; justify-content: center;
        background: #0b1117; color: white;
        animation: slideAway 2.0s forwards; pointer-events: none;
    }
    @keyframes slideAway { 
        0% { opacity: 1; visibility: visible; } 
        80% { opacity: 1; } 
        100% { opacity: 0; visibility: hidden; } 
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE DADOS (BIOLOGIA)
def consultar_dieta_real(classe, nome):
    n = str(nome).lower()
    carnivoros = ['leão', 'tubarão', 'lobo', 'águia', 'falcão', 'orca', 'serpente', 'tigre', 'jacaré', 'raposa', 'gavião', 'polvo', 'coruja', 'sapo', 'rã', 'cobra', 'crocodilo', 'lince', 'leopardo']
    herbivoros = ['elefante', 'veado', 'vaca', 'zebra', 'girafa', 'coelho', 'cavalo', 'ovelha', 'cabra', 'hipopótamo', 'rinoceronte', 'canguru', 'coala', 'panda', 'tartaruga', 'gazela', 'capivara']
    if any(x in n for x in carnivoros): return "Carnívoro (Predador)"
    if any(x in n for x in herbivoros): return "Herbívoro (Plantas/Frutos)"
    return "Omnívoro / Dieta Variada"

def definir_ambiente(classe, nome, local=""):
    n, l = str(nome).lower(), str(local).lower()
    marinhos = ['atlântico', 'pacífico', 'índico', 'ártico', 'mediterrâneo', 'caribe', 'mar', 'oceano', 'barreira']
    if any(x in l for x in marinhos): return "Marinho / Oceânico"
    if any(x in n for x in ['sapo', 'rã', 'jacaré', 'crocodilo', 'sucuri']): return "Ambiente Húmido / Rio"
    return "Terrestre / Florestal"

def buscar_fauna(termo, lat=None, lon=None, local_nome=""):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 24, "locale": "pt-BR", "order_by": "votes"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 800})
    else: params.update({"q": termo})
    try:
        res = requests.get(url, params=params).json()
        lista = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                nome_pt = t.get('preferred_common_name') or t.get('name')
                lista.append({
                    'nome': nome_pt.title(), 'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url'],
                    'classe': t.get('iconic_taxon_name', 'Outros'),
                    'ambiente': definir_ambiente(t.get('iconic_taxon_name', ''), nome_pt, local_nome),
                    'dieta': consultar_dieta_real(t.get('iconic_taxon_name', ''), nome_pt),
                    'repro': "Vivíparo" if 'mammalia' in t.get('iconic_taxon_name','').lower() else "Ovíparo"
                })
        return lista
    except: return []

# BASES DE DATA AMPLIADAS
paises_db = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'],
    'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41],
    'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]
})

florestas_db = pd.DataFrame({
    'nome': [
        'Amazónia (Brasil/Peru)', 'Floresta do Congo (África)', 'Selva de Bornéu (Indonésia)', 
        'Taiga Siberiana (Rússia)', 'Floresta Negra (Alemanha)', 'Daintree (Austrália)', 
        'Tongass (EUA)', 'Monteverde (Costa Rica)', 'Sinharaja (Sri Lanka)', 
        'Mata Atlântica (Brasil)', 'Floresta de Sherwood (Inglaterra)', 'Selva de Valdivia (Chile)'
    ],
    'lat': [-3.46, -0.22, 1.35, 61.52, 48.0, -16.17, 57.17, 10.32, 6.39, -23.55, 53.20, -39.81],
    'lon': [-62.21, 23.61, 113.8, 105.31, 8.0, 145.41, -134.58, -84.79, 80.41, -46.63, -1.07, -73.24]
})

oceanos_db = pd.DataFrame({
    'nome': [
        'Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Oceano Antártico',
        'Mar Mediterrâneo', 'Mar do Caribe', 'Mar Vermelho', 'Grande Barreira de Coral',
        'Mar Morto', 'Mar do Japão', 'Mar de Bering'
    ],
    'lat': [0.0, -15.0, -20.0, 85.0, -70.0, 35.0, 15.0, 20.0, -18.0, 31.5, 35.0, 58.0],
    'lon': [-25.0, -140.0, 70.0, 0.0, 0.0, 18.0, -75.0, 38.0, 147.0, 35.5, 135.0, -170.0]
})

if 'meus_favs_objetos' not in st.session_state: st.session_state.meus_favs_objetos = []
if 'diario' not in st.session_state: st.session_state.diario = ""

# SIDEBAR E CUTSCENE
st.sidebar.title("🌲 MundoVivo")
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas e Selvas", "🌊 Oceanos e Mares", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])
st.markdown(f"<div class='cutscene-overlay'><h1>🚀 A explorar {menu}...</h1></div>", unsafe_allow_html=True)

def desenhar_cartao(a, i, key_prefix):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{a['foto']}' class='img-cc'>
        <div class='common-name'>{a['nome']}</div>
        <div class='sci-name'>{a['sci']}</div>
        <div class='label-expert'>AMBIENTE NATURAL</div><div class='val-expert'>🏡 {a['ambiente']}</div>
        <div class='label-expert'>ALIMENTAÇÃO REAL</div><div class='val-expert'>🍴 {a['dieta']}</div>
        <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
        <div class='label-expert'>CLASSE</div><div class='val-expert'>🏷️ {a['classe']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ Guardar", key=f"{key_prefix}_{i}"):
        if a not in st.session_state.meus_favs_objetos: st.session_state.meus_favs_objetos.append(a)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Global")
    st.map(paises_db, color='#2ea043')
    sel_p = st.selectbox("Escolha um País:", [""] + list(paises_db['nome']))
    if sel_p:
        sel = paises_db[paises_db['nome'] == sel_p].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'], sel_p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "pla")

elif menu == "🌲 Florestas e Selvas":
    st.title("🌲 Florestas e Selvas do Mundo")
    st.map(florestas_db, color='#1e5631')
    f_sel = st.selectbox("Selecione um Bioma Terrestre:", [""] + list(florestas_db['nome']))
    if f_sel:
        sel = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'], f_sel)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "for")

elif menu == "🌊 Oceanos e Mares":
    st.title("🌊 Oceanos e Mares do Planeta")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Selecione um Bioma Marinho:", [""] + list(oceanos_db['nome']))
    if o_sel:
        sel = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'], o_sel)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    p = st.text_input("Pesquisar qualquer animal:")
    if p:
        dados = buscar_fauna(p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário de Observação")
    st.session_state.diario = st.text_area("Regista as tuas descobertas biológicas:", value=st.session_state.diario, height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Coleção de Favoritos")
    if st.button("🗑️ Limpar Todos"): st.session_state.meus_favs_objetos = []; st.rerun()
    cols = st.columns(3)
    for i, a in enumerate(list(st.session_state.meus_favs_objetos)):
        with cols[i%3]:
            desenhar_cartao(a, i, "fav")
            if st.button(f"❌ Eliminar", key=f"del_{i}"):
                st.session_state.meus_favs_objetos.remove(a)
                st.rerun()
