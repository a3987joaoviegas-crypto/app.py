import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA BIOLÓGICA
def definir_biologia(nome, classe, bioma_tipo="geral"):
    n = str(nome).lower()
    dieta = "Omnívoro / Variada"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente', 'crocodilo']):
        dieta = "Carnívoro (Predador)"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda']):
        dieta = "Herbívoro (Plantas)"
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if bioma_tipo == "marinho" else "Terrestre / Florestal"
    return dieta, repro, ambiente

def buscar_fauna(lat, lon, bioma="geral"):
    url = "https://api.inaturalist.org/v1/observations"
    params = {"lat": lat, "lng": lon, "radius": 1500, "taxon_id": 1, "per_page": 15, "locale": "pt-BR"}
    try:
        res = requests.get(url, params=params).json()
        lista = []
        for obs in res.get('results', []):
            t = obs.get('taxon')
            if t and t.get('default_photo'):
                n = t.get('preferred_common_name', t['name']).title()
                d, r, amb = definir_biologia(n, t.get('iconic_taxon_name',''), bioma)
                lista.append({'nome': n, 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        return lista
    except: return []

# DADOS DOS PLANISFÉRIOS
paises_db = pd.DataFrame({'nome': ['Brasil', 'Portugal', 'México', 'Rússia', 'Angola', 'Estados Unidos', 'Canadá', 'Gronelândia', 'Inglaterra', 'Finlândia'], 'lat': [-14.23, 39.39, 23.63, 61.52, -11.20, 37.09, 56.13, 71.70, 52.35, 61.92], 'lon': [-51.92, -8.22, -102.55, 105.31, 17.87, -95.71, -106.34, -42.60, -1.17, 25.74]})
florestas_db = pd.DataFrame({'nome': ['Amazónia', 'Congo', 'Selva de Bornéu', 'Taiga Siberiana', 'Mata Atlântica'], 'lat': [-3.46, -0.22, 1.35, 61.52, -23.55], 'lon': [-62.21, 23.61, 113.8, 105.31, -46.63]})
oceanos_db = pd.DataFrame({'nome': ['Oceano Atlântico', 'Oceano Pacífico', 'Oceano Índico', 'Mar Mediterrâneo'], 'lat': [0.0, -15.0, -20.0, 35.0], 'lon': [-25.0, -140.0, 70.0, 18.0]})

# ESTADOS
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'notas' not in st.session_state: st.session_state.notas = ""
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

# SIDEBAR COM TODAS AS OPÇÕES
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(dados, prefixo, is_zoo=False):
    if not dados: return
    cols = st.columns(3)
    for i, a in enumerate(dados):
        with cols[i%3]:
            st.markdown(f"""<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div><div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {a['ambiente']}</div><div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {a['dieta']}</div><div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div></div>""", unsafe_allow_html=True)
            if not is_zoo:
                if st.button("⭐ Guardar", key=f"add_{prefixo}_{i}"): st.session_state.zoo.append(a)
            else:
                if st.button("🗑️ Eliminar", key=f"del_{prefixo}_{i}"): st.session_state.zoo.pop(i); st.rerun()

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(paises_db)
    sel = st.selectbox("Escolha um País:", [""] + list(paises_db['nome']))
    if sel:
        loc = paises_db[paises_db['nome'] == sel].iloc[0]
        exibir_cartao(buscar_fauna(loc['lat'], loc['lon']), "pla")

elif menu == "🌲 Florestas":
    st.title("🌲 Florestas e Selvas")
    st.map(florestas_db)
    sel = st.selectbox("Escolha uma Selva:", [""] + list(florestas_db['nome']))
    if sel:
        loc = florestas_db[florestas_db['nome'] == sel].iloc[0]
        exibir_cartao(buscar_fauna(loc['lat'], loc['lon'], "floresta"), "flo")

elif menu == "🌊 Oceanos":
    st.title("🌊 Oceanos e Mares")
    st.map(oceanos_db)
    sel = st.selectbox("Escolha um Oceano:", [""] + list(oceanos_db['nome']))
    if sel:
        loc = oceanos_db[oceanos_db['nome'] == sel].iloc[0]
        exibir_cartao(buscar_fauna(loc['lat'], loc['lon'], "marinho"), "oce")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Identificação")
    st.subheader("📸 Analisar Imagem")
    st.file_uploader("Carrega aqui a foto do animal:", type=['jpg','png','jpeg'])
    st.divider()
    st.subheader("🔍 Pesquisa Manual")
    p = st.text_input("Nome do animal para pesquisar dados:")
    if p:
        res = requests.get(f"https://api.inaturalist.org/v1/taxa?q={p}&taxon_id=1&locale=pt-BR").json()
        dados_lab = []
        for t in res.get('results', []):
            if t.get('default_photo'):
                n = t.get('preferred_common_name', t['name']).title()
                d, r, amb = definir_biologia(n, t.get('iconic_taxon_name',''))
                dados_lab.append({'nome': n, 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        exibir_cartao(dados_lab, "lab_man")

elif menu == "💬 Chat IA":
    st.title("💬 Conversa com a IA Bióloga")
    st.write("Descreve as características de um animal ou tira dúvidas sobre biologia.")
    
    for msg in st.session_state.chat_hist:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    user_msg = st.chat_input("Ex: Qual é o animal mais rápido do mundo?")
    if user_msg:
        st.chat_message("user").write(user_msg)
        st.session_state.chat_hist.append({"role": "user", "content": user_msg})
        
        # Lógica de resposta da IA com busca de cartão
        res = requests.get(f"https://api.inaturalist.org/v1/taxa?q={user_msg}&taxon_id=1&locale=pt-BR").json()
        if res['results']:
            t = res['results'][0]
            nome = t.get('preferred_common_name', t['name']).title()
            reply = f"Com base no que disseste, encontrei o **{nome}**. Vê o cartão dele abaixo!"
            st.chat_message("assistant").write(reply)
            st.session_state.chat_hist.append({"role": "assistant", "content": reply})
            d, r, amb = definir_biologia(nome, t.get('iconic_taxon_name',''))
            exibir_cartao([{'nome': nome, 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb}], "chat_ia_card")
        else:
            reply = "Isso parece interessante! Podes descrever melhor as cores ou o habitat desse animal?"
            st.chat_message("assistant").write(reply)
            st.session_state.chat_hist.append({"role": "assistant", "content": reply})

elif menu == "📝 Diário":
    st.title("📝 Diário de Bordo")
    st.session_state.notas = st.text_area("Notas e Observações:", value=st.session_state.notas, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    exibir_cartao(st.session_state.zoo, "zoo_page", is_zoo=True)
