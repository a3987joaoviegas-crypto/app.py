import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# CSS ORIGINAL (O QUE TINHAS ANTES)
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }

    /* CARTÃO ORIGINAL */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-bottom: 25px;
    }
    .img-cc { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 22px; font-weight: bold; margin-top: 10px; text-align: center; }
    .sci-name { color: white; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; margin-top: 5px; text-transform: uppercase;}
    .val-expert { color: white; font-size: 14px; margin-bottom: 6px; }

    /* ESTILO CHAT GEMINI (LIMPO) */
    .stChatMessage { background-color: transparent !important; }
    .stChatMessage [data-testid="stChatMessageContent"] {
        background-color: #1c2128; border-radius: 15px; padding: 15px; border: 1px solid #30363d;
    }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# LÓGICA BIOLÓGICA ORIGINAL
def definir_biologia(nome, classe):
    n = str(nome).lower()
    dieta = "Omnívoro / Variada"
    if any(x in n for x in ['leão', 'tubarão', 'lobo', 'águia', 'orca', 'tigre', 'jacaré', 'serpente']):
        dieta = "Carnívoro (Predador)"
    elif any(x in n for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho', 'canguru', 'panda']):
        dieta = "Herbívoro (Plantas)"
    
    repro = "Vivíparo" if classe == 'Mammalia' else "Ovíparo"
    ambiente = "Marinho / Aquático" if classe in ['Actinopterygii', 'Mollusca'] or "baleia" in n else "Terrestre / Florestal"
    return dieta, repro, ambiente

def buscar_fauna(query, limite=1):
    q = query.lower()
    # Resposta direta para perguntas de recordes
    if "pesado" in q: busca = "Baleia-azul"
    elif "rápido" in q: busca = "Guepardo"
    else: busca = query
    
    url = f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        out = []
        for t in res['results'][:limite]:
            if t.get('default_photo'):
                nome = (t.get('preferred_common_name') or t.get('name')).title()
                classe = t.get('iconic_taxon_name', 'Animal')
                d, r, amb = definir_biologia(nome, classe)
                out.append({'nome': nome, 'sci': t.get('name'), 'foto': t['default_photo']['medium_url'], 'dieta': d, 'repro': r, 'ambiente': amb})
        return out
    except: return []

# ESTADOS
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

# MENU LATERAL
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def exibir_cartao(a, key):
    if not a: return
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
    if st.button("⭐ Guardar no Zoo", key=key):
        st.session_state.zoo.append(a)

# --- PÁGINAS ---

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [-14.2, 39.3], 'lon': [-51.9, -8.2]}))
    animais = buscar_fauna("Brasil", 3)
    cols = st.columns(3)
    for i, an in enumerate(animais):
        with cols[i]: exibir_cartao(an, f"map_{i}")

elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório de Pesquisa")
    txt = st.text_input("🔍 Pesquisar animal ou grupo:")
    if txt:
        lista = buscar_fauna(txt, 12)
        cols = st.columns(3)
        for i, anim in enumerate(lista):
            with cols[i%3]: exibir_cartao(anim, f"lab_{i}")

elif menu == "💬 Chat IA":
    st.title("💬 Chat Biológico")
    for i, msg in enumerate(st.session_state.chat_hist):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "data" in msg: exibir_cartao(msg["data"], f"chat_{i}")

    if p := st.chat_input("Qual o animal mais pesado?"):
        st.session_state.chat_hist.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        with st.chat_message("assistant"):
            dados = buscar_fauna(p, 1)
            if dados:
                resp = f"O animal é o **{dados[0]['nome']}**. Aqui tens o cartão:"
                st.write(resp)
                exibir_cartao(dados[0], "chat_new")
                st.session_state.chat_hist.append({"role": "assistant", "content": resp, "data": dados[0]})

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Notas:", height=400)

elif menu == "⭐ Favoritos":
    st.title("🐾 Meu Zoo")
    cols = st.columns(3)
    for i, z in enumerate(st.session_state.zoo):
        with cols[i%3]: exibir_cartao(z, f"zoo_{i}")
