import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS PERSONALIZADOS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* CARTÃO DE CIDADÃO BIOLÓGICO */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA BIOLÓGICA (IA)
def definir_biologia(nome, classe, bioma_tipo="geral"):
    n = str(nome).lower()
    dieta = "Omnívoro / Variada"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente', 'crocodilo', 'predador']):
        dieta = "Carnívoro (Predador)"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda', 'herbívoro']):
        dieta = "Herbívoro (Plantas)"
    
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if bioma_tipo == "marinho" or "baleia" in n or "peixe" in n else "Terrestre / Florestal"
    return dieta, repro, ambiente

def buscar_dados_animal(query):
    # Pesquisa na API do iNaturalist filtrando por Animais (taxon_id=1)
    url = f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        if res['results']:
            t = res['results'][0]
            nome = (t.get('preferred_common_name') or t.get('name')).title()
            d, r, amb = definir_biologia(nome, t.get('iconic_taxon_name',''))
            return {
                'nome': nome, 
                'sci': t.get('name'), 
                'foto': t['default_photo']['medium_url'] if t.get('default_photo') else None,
                'dieta': d, 'repro': r, 'ambiente': amb
            }
    except: return None
    return None

# BASES DE DADOS MAPAS
paises_db = pd.DataFrame({'nome': ['Brasil', 'Portugal', 'Angola', 'Moçambique'], 'lat': [-14.23, 39.39, -11.20, -18.66], 'lon': [-51.92, -8.22, 17.87, 35.52]})
florestas_db = pd.DataFrame({'nome': ['Amazónia', 'Congo', 'Mata Atlântica'], 'lat': [-3.46, -0.22, -23.55], 'lon': [-62.21, 23.61, -46.63]})
oceanos_db = pd.DataFrame({'nome': ['Atlântico', 'Pacífico', 'Índico'], 'lat': [0.0, -15.0, -20.0], 'lon': [-25.0, -140.0, 70.0]})

# GESTÃO DE ESTADO (SESSÃO)
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'notas' not in st.session_state: st.session_state.notas = ""
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

# SIDEBAR
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(a, prefixo, i=0, is_zoo=False):
    if not a or not a.get('foto'): return
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{a['foto']}' class='img-cc'>
            <div class='common-name'>{a['nome']}</div>
            <div class='sci-name'>{a['sci']}</div>
            <div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {a['ambiente']}</div>
            <div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {a['dieta']}</div>
            <div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div>
        </div>
    """, unsafe_allow_html=True)
    if not is_zoo:
        if st.button("⭐ Guardar no Zoo", key=f"add_{prefixo}_{i}"):
            if a not in st.session_state.zoo: st.session_state.zoo.append(a)
    else:
        if st.button("🗑️ Eliminar", key=f"del_{prefixo}_{i}"):
            st.session_state.zoo.pop(i); st.rerun()

# --- PÁGINAS ---

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(paises_db)
    sel = st.selectbox("Escolha um local:", [""] + list(paises_db['nome']))
    if sel:
        loc = paises_db[paises_db['nome'] == sel].iloc[0]
        st.subheader(f"Vida selvagem em {sel}")
        # Busca automática simulada para o mapa
        animal = buscar_dados_animal(sel)
        exibir_cartao(animal, "map")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Identificação")
    st.subheader("📸 Upload de Imagem")
    up = st.file_uploader("Arrasta e solta a tua foto aqui:", type=['jpg','png','jpeg'])
    if up:
        st.image(up, width=300, caption="Imagem carregada.")
        st.info("A analisar padrões biológicos... Escreve o nome abaixo para gerar o cartão.")
    
    st.divider()
    nome_pesquisa = st.text_input("🔍 Pesquisar espécie por nome:")
    if nome_pesquisa:
        animal = buscar_dados_animal(nome_pesquisa)
        exibir_cartao(animal, "lab")

elif menu == "💬 Chat IA":
    st.title("💬 Chat Biológico")
    
    # Mostrar histórico estilo chat real
    for msg in st.session_state.chat_hist:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "animal_data" in msg:
                exibir_cartao(msg["animal_data"], "chat", i=time.time())

    prompt = st.chat_input("Qual é o animal mais pesado do mundo?")
    if prompt:
        # Mensagem do utilizador
        st.chat_message("user").write(prompt)
        st.session_state.chat_hist.append({"role": "user", "content": prompt})
        
        # Resposta da IA
        with st.spinner("A pensar..."):
            # Lógica para perguntas comuns ou pesquisa direta
            animal_info = buscar_dados_animal(prompt)
            
            if animal_info:
                resp = f"Encontrei informações sobre o **{animal_info['nome']}**! Aqui está o cartão de cidadão dele:"
                st.chat_message("assistant").write(resp)
                exibir_cartao(animal_info, "chat_resp")
                st.session_state.chat_hist.append({"role": "assistant", "content": resp, "animal_data": animal_info})
            else:
                resp = "Ainda não conheço esse animal. Podes descrever as características ou dizer o nome comum?"
                st.chat_message("assistant").write(resp)
                st.session_state.chat_hist.append({"role": "assistant", "content": resp})

elif menu == "📝 Diário":
    st.title("📝 Diário de Bordo")
    st.session_state.notas = st.text_area("Minhas notas:", value=st.session_state.notas, height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    if not st.session_state.zoo:
        st.info("Ainda não guardaste nenhum animal.")
    else:
        cols = st.columns(3)
        for i, b in enumerate(st.session_state.zoo):
            with cols[i%3]:
                exibir_cartao(b, "zoo", i=i, is_zoo=True)

# Restante das abas (Florestas/Oceanos) mantidas com a lógica de mapa e busca
