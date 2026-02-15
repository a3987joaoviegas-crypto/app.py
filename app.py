import streamlit as st
import pandas as pd
import requests
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="MundoVivo", page_icon="🌍", layout="wide")

# ESTILOS
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

def exibir_cartao(dados, prefixo, is_zoo=False):
    if not dados: return
    cols = st.columns(3)
    for i, a in enumerate(dados):
        with cols[i%3]:
            st.markdown(f"""<div class='cc-card'><img src='{a['foto']}' class='img-cc'><div class='common-name'>{a['nome']}</div><div class='sci-name'>{a['sci']}</div><div class='label-expert'>AMBIENTE</div><div class='val-expert'>🏡 {a['ambiente']}</div><div class='label-expert'>DIETA</div><div class='val-expert'>🍴 {a['dieta']}</div><div class='label-expert'>REPRODUÇÃO</div><div class='val-expert'>🧬 {a['repro']}</div><div class='label-expert'>CLASSE</div><div class='val-expert'>🏷️ {a.get('classe', 'Desconhecida')}</div></div>""", unsafe_allow_html=True)
            if not is_zoo:
                if st.button("⭐ Guardar", key=f"add_{prefixo}_{i}"): 
                    if a not in st.session_state.zoo: st.session_state.zoo.append(a)
            else:
                if st.button("🗑️ Eliminar", key=f"del_{prefixo}_{i}"):
                    st.session_state.zoo.pop(i); st.rerun()

# INTERFACE SIDEBAR
if 'zoo' not in st.session_state: st.session_state.zoo = []
menu = st.sidebar.radio("Navegação:", ["🌍 Planisfério", "🔬 Laboratório", "⭐ Favoritos"])

if menu == "🌍 Planisfério":
    st.title("🌍 Planisfério")
    st.info("Explora os mapas para encontrar animais reais.")

elif menu == "🔬 Laboratório":
    st.title("🔬 Identificador com IA")
    
    tab1, tab2 = st.tabs(["📸 Identificar por Foto", "✍️ Identificar por Descrição"])
    
    with tab1:
        img_file = st.file_uploader("Carrega a foto do animal:", type=['jpg', 'png', 'jpeg'])
        if img_file:
            st.image(img_file, caption="A analisar...", width=300)
            st.warning("IA a processar... (Simulação de visão computacional via iNaturalist)")
            # Nota: Para uma IA real de imagem, usaríamos modelos como o TensorFlow/HuggingFace.
            # Aqui simulamos a resposta com base no nome do ficheiro ou sugerimos pesquisa manual.
            st.write("Dica: Escreve o nome provável abaixo para confirmar os dados biológicos.")

    with tab2:
        query = st.text_input("Escreve as características ou nome (ex: Pássaro azul, grande felino...):")
        if query:
            res = requests.get(f"https://api.inaturalist.org/v1/taxa?q={query}&taxon_id=1&locale=pt-BR").json()
            dados_ia = []
            for t in res.get('results', []):
                if t.get('default_photo'):
                    n = t.get('preferred_common_name', t['name']).title()
                    d, r, amb = definir_biologia(n, t.get('iconic_taxon_name',''))
                    dados_ia.append({'nome': n, 'sci': t['name'], 'foto': t['default_photo']['medium_url'], 'classe': t.get('iconic_taxon_name',''), 'dieta': d, 'repro': r, 'ambiente': amb})
                    if len(dados_ia) >= 3: break
            exibir_cartao(dados_ia, "ia_lab")

elif menu == "⭐ Favoritos":
    st.title("🐾 O Meu Zoo")
    exibir_cartao(st.session_state.zoo, "zoo_page", is_zoo=True)
