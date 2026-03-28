import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA
chaves = {
    'zoo': [], 'favoritos': [], 'tanque_fusao': [], 'nomes_zoo': {},
    'pontos_zoologo': 0, 'animais_salvos_ids': set(), 'id_animal_atual': None,
    'internados_vet': [], 
    'c_24h': "", 'c_mega': "", 'premium_ativo': False,
    'cor_tema': "#0b1117", 'negrito': False, 'brilho': 100
}
for k, v in chaves.items():
    if k not in st.session_state: st.session_state[k] = v

# 2. TRADUTOR DE CLASSES
def traduzir_classe(taxon_name):
    traducao = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil", "Amphibia": "Anfíbio", "Actinopterygii": "Peixe", "Arachnida": "Aracnídeo", "Insecta": "Inseto", "Mollusca": "Molusco"}
    return traducao.get(taxon_name, "Espécie Selvagem")

# 3. SISTEMA DE ESTRELAS
def check_stars(pts):
    if pts >= 50000: return "⭐⭐⭐⭐⭐ (Lenda)"
    if pts >= 10000: return "⭐⭐⭐⭐ (Mestre)"
    if pts >= 8000: return "⭐⭐⭐ (Perito)"
    if pts >= 5000: return "⭐⭐ (Veterano)"
    if pts >= 1000: return "⭐ (Iniciado)"
    return "Recruta"

# 4. SIDEBAR
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_ativo = st.session_state.c_24h == "6626"
tem_acesso_vip = is_mega or is_24h_ativo

with st.sidebar:
    st.title("🌍 MundoVivo")
    st.markdown(f"""<div style="background:#1a1c23; padding:15px; border-radius:20px; border:2px solid #ffd700; text-align:center;">
        <p style="margin:0; font-size:0.7em; color:#ffd700;">💳 CARTÃO DE ZOÓLOGO</p>
        <p style="margin:0; font-size:1.2em; font-weight:bold;">{st.session_state.pontos_zoologo} PTS</p>
        <p style="margin:0; font-size:0.9em;">{check_stars(st.session_state.pontos_zoologo)}</p>
    </div>""", unsafe_allow_html=True)
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    
    menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🌀 Salvamento", "🏥 Veterinário", "🔬 Laboratório", "🐾 Meu Zoo", "⭐ Favoritos", "⚙️ Definições"]
    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⭐ Favoritos", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 5. CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background: #1a1c23 !important; border-radius: 25px; padding: 15px; border: 4px solid #2ecc71;
        margin-bottom: 20px; min-height: 400px; text-align: center; opacity: 1 !important;
    }}
    .img-an {{ width: 100%; border-radius: 20px; height: 180px; object-fit: cover; border: 1px solid #444; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 6. FUNÇÃO DO CARTÃO
def card(an, prefixo, idx=0, show_button=True, footer_text=None):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = traduzir_classe(an.get('iconic_taxon_name'))
    
    st.markdown(f"""<div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.7em;">💳 CARTÃO DE CIDADÃO</span>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome}</h3>
        <p style="margin:2px 0;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0;">🥚 <b>Repro:</b> {"Ovíparo" if classe != "Mamífero" else "Vivíparo"}</p>
        {f'<p style="color:#ffd700; font-weight:bold;">{footer_text}</p>' if footer_text else ''}
    </div>""", unsafe_allow_html=True)
    
    if show_button:
        if st.button("📥 Zoo", key=f"btn_{prefixo}_{idx}", use_container_width=True):
            st.session_state.zoo.append(an); st.toast(f"{nome} adicionado!")

# 7. ABAS
if aba == "🌀 Salvamento":
    st.header("🌀 Centro de Emergência")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    
    if st.session_state.id_animal_atual is None:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={random.choice(['Africa','Amazon','Australia'])}&taxon_id=1&per_page=50&locale=pt-PT")
        validos = [a for a in r.json()['results'] if a['id'] not in st.session_state.animais_salvos_ids]
        if validos: st.session_state.id_animal_atual = random.choice(validos)

    if st.session_state.id_animal_atual:
        an = st.session_state.id_animal_atual
        nome_resgate = (an.get('preferred_common_name') or an.get('name')).title()
        
        st.warning(f"🆘 ALERTA CRÍTICO: Um **{nome_resgate}** foi detetado com ferimentos graves!")
        card(an, "resgate", 0, show_button=False)
        
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.pontos_zoologo += 50
            st.session_state.animais_salvos_ids.add(an['id'])
            alta = datetime.now() + timedelta(hours=24)
            st.session_state.internados_vet.append({'animal': an, 'data_alta': alta.timestamp()})
            st.session_state.id_animal_atual = None
            st.success("Resgate efetuado! Animal em observação no Veterinário.")
            st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital Veterinário")
    if not st.session_state.internados_vet:
        st.info("O hospital está vazio. Todos os animais estão saudáveis!")
    else:
        for i in range(0, len(st.session_state.internados_vet), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(st.session_state.internados_vet):
                    item = st.session_state.internados_vet[i+j]
                    an = item['animal']
                    falta = item['data_alta'] - datetime.now().timestamp()
                    
                    with cols[j]:
                        if falta > 0:
                            h = int(falta // 3600)
                            m = int((falta % 3600) // 60)
                            txt_tempo = f"⏳ Alta em: {h}h {m}m"
                            card(an, "vet_list", i+j, show_button=False, footer_text=txt_tempo)
                        else:
                            card(an, "vet_list", i+j, show_button=False, footer_text="✅ Recuperado!")
                            if st.button("🏁 Mover para Zoo", key=f"move_{i+j}", use_container_width=True):
                                st.session_state.zoo.append(an)
                                st.session_state.internados_vet.pop(i+j)
                                st.rerun()

elif aba == "🔬 Laboratório":
    busca = st.text_input("🔍 Analisar Espécie:")
    if busca:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&per_page=70&locale=pt-PT")
        animais = r.json().get('results', [])
        for i in range(0, len(animais), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(animais):
                    with cols[j]: card(animais[i+j], "lab", i+j)

elif aba == "🐾 Meu Zoo":
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[i+j], "zoo", i+j)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    st.session_state.brilho = st.slider("Brilho", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
