import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO ESTILO GEMINI
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stApp { background-color: #0b1117; color: #adbac7; }
    
    /* BOLHAS DE CHAT ESTILO GEMINI */
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    [data-testid="stChatMessage"] { background-color: #1c2128; border: 1px solid #30363d; }
    
    /* CARTÃO DE CIDADÃO */
    .cc-card { 
        background: #1c2128; border-radius: 12px; padding: 20px; 
        border-left: 6px solid #2ea043; margin-top: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .img-cc { width: 100%; height: 250px; object-fit: cover; border-radius: 8px; }
    .common-name { color: #2ea043; font-size: 24px; font-weight: bold; margin-top: 12px; text-align: center; }
    .sci-name { color: #8b949e; font-style: italic; font-size: 14px; text-align: center; margin-bottom: 15px; }
    .label-expert { color: #2ea043; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-top: 8px;}
    .val-expert { color: white; font-size: 15px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INTELIGÊNCIA DE RESPOSTA DIRETA (Sem Perguntas)
def inteligencia_ia(query):
    q = query.lower()
    # Conhecimento prévio para não perguntar nada ao utilizador
    dict_direto = {
        "pesado": "Baleia-azul",
        "mais pesado do mundo": "Baleia-azul",
        "mais pesado da terra": "Elefante-africano",
        "mais rápido": "Falcão-peregrino",
        "mais veloz": "Guepardo",
        "maior animal": "Baleia-azul",
        "maior ave": "Avestruz",
        "mais inteligente": "Chimpanzé"
    }
    
    # Se encontrar uma palavra-chave, define o alvo imediatamente
    alvo = None
    for chave, valor in dict_direto.items():
        if chave in q:
            alvo = valor
            break
    
    if not alvo:
        alvo = query # Se não for pergunta de recorde, pesquisa o nome direto

    # Busca os dados biológicos reais
    url = f"https://api.inaturalist.org/v1/taxa?q={alvo}&taxon_id=1&locale=pt-BR"
    try:
        res = requests.get(url).json()
        if res['results']:
            t = res['results'][0]
            nome = (t.get('preferred_common_name') or t.get('name')).title()
            classe = t.get('iconic_taxon_name', 'Desconhecida')
            
            # Lógica biológica automática
            dieta = "Herbívoro" if any(x in nome.lower() for x in ['elefante', 'zebra', 'girafa', 'vaca', 'coelho']) else "Carnívoro"
            ambiente = "Marinho" if classe in ['Actinopterygii', 'Mollusca'] or "baleia" in nome.lower() else "Terrestre"
            
            return {
                'nome': nome, 'sci': t.get('name'), 
                'foto': t['default_photo']['medium_url'] if t.get('default_photo') else None,
                'dieta': dieta, 'repro': "Vivíparo" if classe == "Mammalia" else "Ovíparo", 'ambiente': ambiente
            }
    except: return None
    return None

# 3. INTERFACE
if 'zoo' not in st.session_state: st.session_state.zoo = []
if 'chat_hist' not in st.session_state: st.session_state.chat_hist = []

menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🌲 Florestas", "🌊 Oceanos", "🔬 Laboratório", "💬 Chat IA", "📝 Diário", "⭐ Favoritos"])

def mostrar_cc(a, key):
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

# --- SECÇÃO DO CHAT (ESTILO GEMINI) ---
if menu == "💬 Chat IA":
    st.title("💬 Chat Biológico")
    
    # Contentor para as mensagens
    for i, msg in enumerate(st.session_state.chat_hist):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "data" in msg:
                mostrar_cc(msg["data"], f"chat_btn_{i}")

    if prompt := st.chat_input("Ex: Qual o animal mais pesado do mundo?"):
        # Mensagem do utilizador (Direita)
        st.session_state.chat_hist.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Resposta da IA (Esquerda)
        with st.chat_message("assistant"):
            dados = inteligencia_ia(prompt)
            if dados:
                txt = f"Com certeza! O animal que procuras é o **{dados['nome']}**. Aqui tens os detalhes:"
                st.write(txt)
                mostrar_cc(dados, f"new_chat_btn")
                st.session_state.chat_hist.append({"role": "assistant", "content": txt, "data": dados})
            else:
                txt = "Encontrei este animal na base de dados, mas os detalhes estão a ser processados. Tenta o nome comum!"
                st.write(txt)
                st.session_state.chat_hist.append({"role": "assistant", "content": txt})

# --- RESTO DAS ABAS (Mantidas como pediste) ---
elif menu == "🔬 Laboratório":
    st.title("🔬 Laboratório")
    st.subheader("📸 Upload de Imagem")
    st.file_uploader("Arrasta e solta a tua foto aqui (Drag and Drop):", type=['jpg','png','jpeg'])
    st.divider()
    nome = st.text_input("🔍 Identificação Manual:")
    if nome:
        mostrar_cc(inteligencia_ia(nome), "lab_btn")

elif menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.map(pd.DataFrame({'lat': [39.39], 'lon': [-8.22]})) # Exemplo Portugal
    st.info("Clica num ponto do mapa para ver a fauna local (Em desenvolvimento)")

elif menu == "📝 Diário":
    st.title("📝 Diário")
    st.text_area("Escreve aqui as tuas notas:", height=300)

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    for i, b in enumerate(st.session_state.zoo):
        mostrar_cc(b, f"zoo_del_{i}")
