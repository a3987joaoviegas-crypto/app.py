import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'tanque_fusao': [], 'pontos_zoologo': 0, 
    'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 'c_24h': "", 'c_mega': "", 
    'premium_ativo': False, 'cor_tema': "#0b1117", 'brilho': 100,
    'inicio_sessao_24h': None
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. LÓGICA DE CÓDIGOS E TEMPO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_valido = False
if st.session_state.c_24h == "6626":
    if st.session_state.inicio_sessao_24h is None:
        st.session_state.inicio_sessao_24h = datetime.now().timestamp()
    
    tempo_passado = datetime.now().timestamp() - st.session_state.inicio_sessao_24h
    if tempo_passado < 86400: # 24 horas
        is_24h_valido = True
    else:
        st.session_state.c_24h = "" # Expira o código

tem_acesso_vip = is_mega or is_24h_valido

# 3. DEFINIÇÃO DE BORDAS (CSS DINÂMICO)
borda_style = "4px solid #2ecc71" # Padrão
if is_mega:
    borda_style = "4px solid; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;"
    anim_rainbow = """
    @keyframes rainbow { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
    .cartao-cidadao { animation: rainbow 3s linear infinite; }
    """
elif is_24h_valido:
    borda_style = "4px solid #ffd700"
    anim_rainbow = ""
else:
    anim_rainbow = ""

# 4. CSS
st.markdown(f"""
<style>
    {anim_rainbow}
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; border-radius: 25px; padding: 15px; 
        border: {borda_style}; margin-bottom: 20px; text-align: center; color: white;
    }}
    .img-an {{ width: 100%; border-radius: 20px; height: 180px; object-fit: cover; border: 1px solid #444; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 5. TRADUTOR E CLASSES
def traduzir_classe(taxon_name):
    traducao = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio", "Actinopterygii": "Peixe", "Arachnida": "Aracnídeo", "Insecta": "Inseto", "Mollusca": "Molusco"}
    return traducao.get(taxon_name, "Espécie Selvagem")

def check_stars(pts):
    if pts >= 50000: return "⭐⭐⭐⭐⭐ (Lenda)"
    if pts >= 1000: return "⭐ (Iniciado)"
    return "Recruta"

# 6. FUNÇÃO DO CARTÃO (COM BOTÃO DNA)
def card(an, prefixo, idx=0, show_button=True, footer_text=None, is_zoo=False):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = traduzir_classe(an.get('iconic_taxon_name'))
    
    st.markdown(f"""<div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.7em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome}</h3>
        <p style="margin:2px 0;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0;">🥩 <b>Alim:</b> {random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])}</p>
        {f'<p style="color:#ffd700; font-weight:bold;">{footer_text}</p>' if footer_text else ''}
    </div>""", unsafe_allow_html=True)
    
    if show_button:
        c1, c2 = st.columns(2)
        with c1:
            if is_zoo:
                if st.button("🗑️ Excluir", key=f"del_{prefixo}_{idx}"):
                    st.session_state.zoo.pop(idx); st.rerun()
            else:
                if st.button("📥 Zoo", key=f"in_{prefixo}_{idx}"):
                    st.session_state.zoo.append(an); st.toast("Adicionado!")
        with c2:
            if st.button("🧬 DNA", key=f"dna_{prefixo}_{idx}"):
                st.session_state.tanque_fusao.append(an); st.toast("Enviado para Fusão!")

# 7. SIDEBAR
with st.sidebar:
    st.title("🌍 MundoVivo")
    if is_24h_valido:
        restante = 86400 - (datetime.now().timestamp() - st.session_state.inicio_sessao_24h)
        st.caption(f"⏳ Tempo Premium: {int(restante//3600)}h {int((restante%3600)//60)}m")
    
    st.markdown(f"""<div style="background:#1a1c23; padding:15px; border-radius:20px; border:2px solid #ffd700; text-align:center;">
        <p style="margin:0; font-size:1.2em; font-weight:bold;">{st.session_state.pontos_zoologo} PTS</p>
        <p style="margin:0; font-size:0.9em;">{check_stars(st.session_state.pontos_zoologo)}</p>
    </div>""", unsafe_allow_html=True)
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 8. LOGICA DE ABAS (SIMPLIFICADA PARA O CODIGO)
if aba == "🧬 Tanque de Fusão":
    st.header("🧬 Tanque de Fusão Genética")
    if len(st.session_state.tanque_fusao) < 2:
        st.info("Envie pelo menos 2 animais via botão DNA para realizar a fusão.")
    else:
        opcoes = { (a.get('preferred_common_name') or a.get('name')).title(): a for a in st.session_state.tanque_fusao }
        ani1 = st.selectbox("Animal 1 (Mãe):", list(opcoes.keys()), key="f1")
        ani2 = st.selectbox("Animal 2 (Pai):", list(opcoes.keys()), key="f2")
        
        if st.button("🔬 INICIAR FUSÃO"):
            a1, a2 = opcoes[ani1], opcoes[ani2]
            nome_cientifico = f"{a1.get('name').split()[0]} {a2.get('name').split()[-1]}"
            st.success(f"Nova espécie criada: **{nome_cientifico}**!")
            st.balloons()

elif aba == "🌀 Salvamento":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if st.session_state.id_animal_atual is None:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={random.choice(['Africa','Amazon'])}&taxon_id=1&per_page=1&locale=pt-PT")
        if r.json()['results']: st.session_state.id_animal_atual = r.json()['results'][0]
    if st.session_state.id_animal_atual:
        card(st.session_state.id_animal_atual, "res", 0, show_button=False)
        if st.button("🚁 RESGATAR"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.pontos_zoologo += 50
            st.session_state.internados_vet.append({'animal': st.session_state.id_animal_atual, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None
            st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital Veterinário")
    for i, item in enumerate(st.session_state.internados_vet):
        falta = item['data_alta'] - datetime.now().timestamp()
        if falta > 0:
            card(item['animal'], "vet", i, show_button=False, footer_text=f"⏳ {int(falta//3600)}h {int((falta%3600)//60)}m")
        else:
            card(item['animal'], "vet", i, show_button=False, footer_text="✅ PRONTO!")
            if st.button("🏁 Zoo", key=f"mv_{i}"):
                st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(i); st.rerun()

elif aba == "🐾 Meu Zoo":
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j, is_zoo=True)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    st.session_state.brilho = st.slider("Brilho", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
