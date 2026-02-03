import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA (Sidebar sempre aberta por padrão)
st.set_page_config(
    page_title="MundoVivo", 
    page_icon="🌍", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ESTILOS: LIMPEZA E FOCO NOS CARTÕES
st.markdown("""
    <style>
    /* Remover apenas o que é estritamente necessário para não quebrar a sidebar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* ESTILO DOS CARTÕES */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 6px; }

    /* CUTSCENE */
    .cutscene-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: radial-gradient(circle, #062814 0%, #0b1117 100%);
        color: #2ea043; text-align: center;
        animation: fadeOutScene 2.5s forwards; pointer-events: none;
    }
    @keyframes fadeOutScene { 0% { opacity: 1; } 80% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA BIOLÓGICA
def definir_biologia(nome, classe, bioma_tipo):
    n = str(nome).lower()
    dieta = "Omnívoro / Variada"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente', 'crocodilo']):
        dieta = "Carnívoro (Predador)"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda']):
        dieta = "Herbívoro (Plantas)"
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if bioma_tipo == "marinho" else "Terrestre / Florestal"
    return dieta, repro, ambiente

def buscar_fauna_filtrada(lat, lon, bioma_tipo):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"lat": lat, "lng": lon, "radius": 1200, "taxon_id": 1, "per_page": 60, "locale": "pt-BR"}
    try:
        res = requests.get(url, params=params).json()
        lista = []
        v_ids = set(); v_nomes = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if not t or not t.get('default_photo'): continue
            tid = t.get('id'); npt = (t.get('preferred_common_name') or t.get('name')).title()
            if tid in v_ids or npt in v_nomes: continue
            classe = t.get('iconic_taxon_name', '')
            d, r, amb = definir_biologia(npt, classe, bioma_tipo)
            lista.append({'nome': npt, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'classe': classe, 'dieta': d, 'repro': r, 'ambiente': amb})
            v_ids.add(tid); v_nomes.add(npt)
            if len(lista) >= 15: break
        return lista
    except: return []

# DADOS
paises_db = pd.DataFrame({'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia', 'Maldivas', 'Saara'], 'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92, 3.20, 23.41], 'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74, 73.22, 25.66]})
florestas_db = pd.DataFrame({'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Mata Atlântica', 'Daintree Rainforest'], 'lat': [-3.46, -0.22, 1.35, 61.52, -23.55, -16.17], 'lon': [-62.21, 23.61, 113.8, 105.31, -46.63, 145.41]})
oceanos_db = pd.DataFrame({'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Oceano Ártico', 'Mar Mediterrâneo', 'Mar do Caribe'], 'lat': [0.0, -15.0, -20.0, 85.0, 35.0, 15.0], 'lon': [-25.0, -140.0, 70.0, 0.0, 18.0, -75.0]})

if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'notas' not in st.session_state: st.session_state.notas = ""

# A SIDEBAR É DEFINIDA AQUI
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(dados, prefixo, is_zoo=False):
    cols = st.columns(3)
    for i, a in enumerate(dados):
        with cols[i%3]:
            st.markdown(f"""<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div><div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {a['ambiente']}</div><div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {a['dieta']}</div><div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div><div class='label-expert'>CLASSE</div><div class='val-expert'>🏷️ {a.get('classe', 'Desconhecida')}</div></div>""", unsafe_allow_html=True)
            if not is_zoo:
                if st.button("⭐ Guardar no Zoo", key=f"add_{prefixo}_{i}"): 
                    if a not in st.session_state.zoo: st.session_state.zoo.append(a)
            else:
                if st.button("🗑️ Eliminar do Zoo", key=f"del_{prefixo}_{i}"):
                    st.session_state.zoo.pop(i); st.rerun()

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(paises_db)
    sel = st.selectbox("Escolha a Região:", [""] + list(paises_db['nome']))
    if sel:
        st.markdown(f'<div class="cutscene-overlay" key="{sel}_{time.time()}"><h1>🌍 A viajar para...</h1><h2>{sel}</h2></div>', unsafe_allow_html=True)
        st.subheader(f"🐾 Espécies em: {sel}")
        loc = paises_db[paises_db['nome'] == sel].iloc[0]
        exibir_cartao(buscar_fauna_filtrada(loc['lat'], loc['lon'], "geral"), "pla")

elif menu == "🌲 Florestas":
    st.title("🌲 Florestas e Selvas")
    st.map(florestas_db, color='#2ea043')
    f_sel = st.selectbox("Escolha a Selva:", [""] + list(florestas_db['nome']))
    if f_sel:
        st.markdown(f'<div class="cutscene-overlay" key="{f_sel}_{time.time()}"><h1>🌲 A entrar na selva...</h1><h2>{f_sel}</h2></div>', unsafe_allow_html=True)
        st.subheader(f"🌲 Vida Selvagem: {f_sel}")
        loc = florestas_db[florestas_db['nome'] == f_sel].iloc[0]
        exibir_cartao(buscar_fauna_filtrada(loc['lat'], loc['lon'], "floresta"), "for")

elif menu == "🌊 Oceanos":
    st.title("🌊 Oceanos e Mares")
    st.map(oceanos_db, color='#0077be')
    o_sel = st.selectbox("Escolha o Mar:", [""] + list(oceanos_db['nome']))
    if o_sel:
        st.markdown(f'<div class="cutscene-overlay" key="{o_sel}_{time.time()}"><h1>🌊 A mergulhar no...</h1><h2>{o_sel}</h2></div>', unsafe_allow_html=True)
        st.subheader(f"🌊 Profundezas de: {o_sel}")
        loc = oceanos_db[oceanos_db['nome'] == o_sel].iloc[0]
        exibir_cartao(buscar_fauna_filtrada(loc['lat'], loc['lon'], "marinho"), "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisa")
    p = st.text_input("Nome do animal:")
    if p:
        res = requests.get(f"https://api.inaturalist.org/v1/observations?q={p}&per_page=12&locale=pt-BR").json()
        dados_lab = []; v_n = set()
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                n = t.get('preferred_common_name', t['name']).title()
                if n in v_n: continue
                d, r, amb = definir_biologia(n, t.get('iconic_taxon_name',''), "geral")
                dados_lab.append({'nome': n, 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'classe': t.get('iconic_taxon_name',''), 'dieta': d, 'repro': r, 'ambiente': amb})
                v_n.add(n)
        exibir_cartao(dados_lab, "lab")

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.session_state.notas = st.text_area("Notas:", value=st.session_state.notas, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Pequeno Zoo")
    if st.session_state.zoo:
        if st.button("🗑️ Limpar Todo o Zoo"):
            st.session_state.zoo = []; st.rerun()
        exibir_cartao(st.session_state.zoo, "zoo_page", is_zoo=True)
    else:
        st.info("O teu zoo está vazio!")
