import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS REFORÇADOS (ESTILO GEMINI + MAPA)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* CHAT ESTILO GEMINI */
    .stChatMessage { border-radius: 20px; padding: 20px; margin-bottom: 15px; }
    
    /* CARTÃO DE CIDADÃO BIOLÓGICO */
    .cc-card { 
        background: #1c2128; border-radius: 15px; padding: 25px; 
        border-left: 8px solid #2ea043; margin-top: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.6);
    }
    .img-cc { width: 100%; height: 280px; object-fit: cover; border-radius: 10px; }
    .common-name { color: #2ea043; font-size: 26px; font-weight: bold; margin-top: 15px; text-align: center; }
    .sci-name { color: #8b949e; font-style: italic; text-align: center; margin-bottom: 20px; }
    .expert-box { display: flex; flex-wrap: wrap; justify-content: space-between; }
    .item-expert { width: 45%; margin-bottom: 10px; }
    .label-expert { color: #2ea043; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .val-expert { color: white; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA DE INTELIGÊNCIA SEM PERGUNTAS
def pensar_como_ia(query):
    q = query.lower()
    # Mapeamento direto de respostas para perguntas de recordes
    if "pesado" in q:
        busca = "Baleia-azul" if "mar" in q or "mundo" in q else "Elefante-africano"
    elif "rápido" in q or "veloz" in q:
        busca = "Guepardo" if "terra" in q else "Falcão-peregrino"
    else:
        busca = query

    url = f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        if res['results']:
            t = res['results'][0]
            nome = (t.get('preferred_common_name') or t.get('name')).title()
            classe = t.get('iconic_taxon_name', '')
            
            # Automação biológica para o cartão
            dieta = "Herbívoro" if any(x in nome.lower() for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru']) else "Carnívoro / Omnívoro"
            ambiente = "Marinho" if classe in ['Actinopterygii', 'Mollusca'] or "baleia" in nome.lower() else "Terrestre / Florestal"
            
            return {
                'nome': nome, 'sci': t.get('name'), 
                'foto': t['default_photo']['medium_url'] if t.get('default_photo') else "https://via.placeholder.com/300",
                'dieta': dieta, 'repro': "Vivíparo" if classe == "Mammalia" else "Ovíparo", 'ambiente': ambiente
            }
    except: return None
    return None

# DADOS DO MAPA MUNDO (RESTAURADOS)
mapa_data = pd.DataFrame({
    'nome': ['Brasil', 'Portugal', 'Angola', 'Moçambique', 'Estados Unidos', 'Austrália', 'Índia', 'Egito'],
    'lat': [-14.23, 39.39, -11.20, -18.66, 37.09, -25.27, 20.59, 26.82],
    'lon': [-51.92, -8.22, 17.87, 35.52, -95.71, 133.77, 78.96, 30.80]
})

# SESSÃO
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

# MENU LATERAL
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def render_cartao(dados, key):
    if not dados: return
    st.markdown(f"""
        <div class='cc-card'>
            <img src='{dados['foto']}' class='img-cc'>
            <div class='common-name'>{dados['nome']}</div>
            <div class='sci-name'>{dados['sci']}</div>
            <div class='expert-box'>
                <div class='item-expert'><div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {dados['ambiente']}</div></div>
                <div class='item-expert'><div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {dados['dieta']}</div></div>
                <div class='item-expert'><div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {dados['repro']}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⭐ Guardar no Meu Zoo", key=key):
        st.session_state.zoo.append(dados)
        st.success("Guardado!")

# --- PLANISFÉRIO (O MAPA QUE FALTAVA) ---
if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério Bio-Interativo")
    st.map(mapa_data)
    sel = st.selectbox("Explorar Fauna do País:", [""] + list(mapa_data['nome']))
    if sel:
        with st.spinner(f"A viajar para {sel}..."):
            animal = pensar_como_ia(sel)
            render_cartao(animal, "map_btn")

# --- CHAT IA (ESTILO GEMINI REAL) ---
elif menu == "💬 Chat IA":
    st.title("💬 Chat Inteligente")
    
    for i, msg in enumerate(st.session_state.chat_hist):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "data" in msg:
                render_cartao(msg["data"], f"chat_btn_{i}")

    if prompt := st.chat_input("Ex: Qual é o animal mais pesado do mundo?"):
        st.session_state.chat_hist.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            dados = pensar_como_ia(prompt)
            if dados:
                txt = f"Com base no conhecimento biológico, o animal que procuras é o **{dados['nome']}**."
                st.write(txt)
                render_cartao(dados, "chat_new")
                st.session_state.chat_hist.append({"role": "assistant", "content": txt, "data": dados})
            else:
                st.write("Não consegui encontrar dados específicos, mas estou a aprender!")

# --- LABORATÓRIO (DRAG AND DROP) ---
elif menu == "🔬 Laboratório":
    st.title("🔬 Identificação Avançada")
    st.subheader("📸 Upload e Análise")
    foto = st.file_uploader("Arraste aqui a sua foto (Drag and Drop):", type=['jpg','png','jpeg'])
    if foto:
        st.image(foto, width=400)
        st.success("Imagem carregada com sucesso para análise.")
    st.divider()
    nome_man = st.text_input("🔍 Ou pesquise o animal manualmente:")
    if nome_man:
        render_cartao(pensar_como_ia(nome_man), "lab_man")

# --- OUTRAS ABAS ---
elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Notas:", height=400, placeholder="Escreve aqui as tuas observações sobre os animais...")

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    if not st.session_state.zoo:
        st.info("O teu zoo está vazio.")
    else:
        for i, z in enumerate(st.session_state.zoo):
            render_cartao(z, f"zoo_del_{i}")
