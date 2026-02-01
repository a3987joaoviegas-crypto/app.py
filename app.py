import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS, SEGURANÇA E ANIMAÇÕES
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
    .label-expert { color: #2ea043; font-weight: bold; font-size: 13px; margin-top: 8px;}
    .val-expert { color: white; font-size: 15px; margin-bottom: 4px; }

    /* CUTSCENE GERAL */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 9999; display: flex; align-items: center; justify-content: center;
        background: #0b1117; color: white;
        animation: slideAway 1.5s forwards; pointer-events: none;
    }
    @keyframes slideAway {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE FILTRAGEM POR AMBIENTE REAL
def definir_ambiente(classe, nome, local_nome=""):
    n = str(nome).lower()
    local = str(local_nome).lower()
    if any(x in local for x in ['saara', 'deserto']): return "Árido / Deserto"
    if any(x in n for x in ['tubarão', 'peixe', 'orca', 'baleia', 'lula', 'coral']) or "oceano" in local: return "Marinho / Aquático"
    if any(x in n for x in ['sapo', 'rã', 'jacaré', 'crocodilo', 'hipopótamo']): return "Ambiente Húmido"
    return "Terrestre / Florestal"

def buscar_fauna(termo, lat=None, lon=None, local_nome=""):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"taxon_id": 1, "per_page": 24, "locale": "pt-BR"}
    if lat and lon: params.update({"lat": lat, "lng": lon, "radius": 500})
    else: params.update({"q": termo})
    try:
        res = requests.get(url, params=params).json()
        lista = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                ambiente = definir_ambiente(t.get('iconic_taxon_name', ''), t.get('name'), local_nome)
                # Filtro rigoroso para o Saara
                if local_nome == "Saara" and ambiente != "Árido / Deserto": continue
                
                lista.append({
                    'nome': (t.get('preferred_common_name') or t.get('name')).title(),
                    'sci': t.get('name'),
                    'foto': t['default_photo']['medium_url'],
                    'ambiente': ambiente,
                    'dieta': "Específica da Espécie",
                    'repro': "Vivíparo" if 'mammalia' in t.get('iconic_taxon_name','').lower() else "Ovíparo"
                })
        return lista
    except: return []

# BASES DE DADOS
paises_db = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'],
    'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41],
    'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]
})

if 'meus_favs_objetos' not in st.session_state: st.session_state.meus_favs_objetos = []
if 'diario' not in st.session_state: st.session_state.diario = ""

# SIDEBAR E CUTSCENE DE NAVEGAÇÃO
st.sidebar.title("🌲 MundoVivo")
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas do Mundo", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])
st.markdown(f"<div class='cutscene-overlay'><h1>🚀 A carregar {menu}...</h1></div>", unsafe_allow_html=True)

def desenhar_cartao(a, i, key_prefix):
    st.markdown(f"""
    <div class='cc-card'>
        <img src='{a['foto']}' class='img-cc'>
        <h3>{a['nome']}</h3>
        <div class='label-expert'>AMBIENTE NATURAL</div><div class='val-expert'>{a['ambiente']}</div>
        <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>{a['repro']}</div>
        <div class='label-expert'>CIENTÍFICO</div><div class='val-expert'><i>{a['sci']}</i></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"⭐ Guardar", key=f"{key_prefix}_{i}"):
        if a not in st.session_state.meus_favs_objetos: st.session_state.meus_favs_objetos.append(a)

# INTERFACES
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Global")
    st.map(paises_db, color='#2ea043')
    sel_p = st.selectbox("Escolha o País:", [""] + list(paises_db['nome']))
    if sel_p:
        sel = paises_db[paises_db['nome'] == sel_p].iloc[0]
        dados = buscar_fauna("", sel['lat'], sel['lon'], sel_p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "pla")

elif menu == "🌲 Florestas do Mundo":
    st.title("🌲 Exploração Florestal")
    f_sel = st.selectbox("Escolha a Floresta:", ["", "Amazónia", "Congo", "Taiga"])
    if f_sel:
        dados = buscar_fauna(f_sel, local_nome="Floresta")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "for")

elif menu == "🌊 Oceanos":
    st.title("🌊 Oceanos")
    o_sel = st.selectbox("Escolha o Oceano:", ["", "Oceano Atlântico", "Oceano Pacífico"])
    if o_sel:
        dados = buscar_fauna("", local_nome="Oceano")
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    p = st.text_input("Pesquisar:")
    if p:
        dados = buscar_fauna(p)
        cols = st.columns(3)
        for i, a in enumerate(dados):
            with cols[i%3]: desenhar_cartao(a, i, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.session_state.diario = st.text_area("Notas:", value=st.session_state.diario, height=400)

elif menu == "⭐ Favoritos":
    st.title("⭐ Favoritos")
    if st.button("🗑️ Eliminar Todos"): st.session_state.meus_favs_objetos = []; st.rerun()
    cols = st.columns(3)
    for i, a in enumerate(list(st.session_state.meus_favs_objetos)):
        with cols[i%3]:
            desenhar_cartao(a, i, "fav")
            if st.button(f"❌ Eliminar", key=f"del_{i}"):
                st.session_state.meus_favs_objetos.remove(a)
                st.rerun()
