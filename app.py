import streamlit as st
import requests
import random
import time
from datetime import datetime, timedelta

# 1. ESTADO DO SISTEMA (FAVORITOS REMOVIDOS)
chaves = {
    'zoo': [], 'tanque_fusao': [], 'nomes_zoo': {},
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

# 4. LÓGICA DE ACESSO
is_mega = st.session_state.c_mega == "67lucas62"
is_24h_ativo = st.session_state.c_24h == "6626"
tem_acesso_vip = is_mega or is_24h_ativo

# 5. SIDEBAR (SEM FAVORITOS)
with st.sidebar:
    st.title("🌍 MundoVivo")
    st.markdown(f"""<div style="background:#1a1c23; padding:15px; border-radius:20px; border:2px solid #ffd700; text-align:center;">
        <p style="margin:0; font-size:0.7em; color:#ffd700;">💳 CARTÃO DE ZOÓLOGO</p>
        <p style="margin:0; font-size:1.2em; font-weight:bold;">{st.session_state.pontos_zoologo} PTS</p>
        <p style="margin:0; font-size:0.9em;">{check_stars(st.session_state.pontos_zoologo)}</p>
    </div>""", unsafe_allow_html=True)
    
    if tem_acesso_vip:
        st.session_state.premium_ativo = st.toggle("✨ MODO PREMIUM", value=st.session_state.premium_ativo)
    else:
        st.session_state.premium_ativo = False

    if st.session_state.premium_ativo:
        menu = ["🌀 Salvamento", "🏥 Veterinário", "🧬 Tanque de Fusão", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    else:
        menu = ["🌲 Florestas", "🌊 Oceanos", "🏳️ Países", "🔬 Laboratório", "🐾 Meu Zoo", "⚙️ Definições"]
    aba = st.radio("Navegação", menu)

# 6. DESIGN CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {st.session_state.cor_tema}; filter: brightness({st.session_state.brilho/100}); }}
    .cartao-cidadao {{
        background-color: #1a1c23 !important; border-radius: 25px; padding: 15px; border: 4px solid #2ecc71;
        margin-bottom: 20px; text-align: center; color: white; opacity: 1 !important;
    }}
    .img-an {{ width: 100%; border-radius: 20px; height: 180px; object-fit: cover; border: 1px solid #444; }}
    @keyframes helicopter_ride {{ 0% {{ transform: translateX(-200px); }} 100% {{ transform: translateX(110vw); }} }}
    .heli-anim {{ position: fixed; top: 30%; font-size: 80px; z-index: 9999; animation: helicopter_ride 3s linear forwards; }}
</style>
""", unsafe_allow_html=True)

# 7. FUNÇÃO DO CARTÃO
def card(an, prefixo, idx=0, show_button=True, footer_text=None, is_zoo=False):
    if not an: return
    nome = (an.get('preferred_common_name') or an.get('name', 'Espécie')).title()
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = traduzir_classe(an.get('iconic_taxon_name'))
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    
    html_cartao = f"""
    <div class="cartao-cidadao">
        <span style="color:#ffd700; font-weight:bold; font-size:0.7em;">💳 CARTÃO DE CIDADÃO</span><br>
        <img src="{foto}" class="img-an">
        <h3 style="color:#ffd700; margin:10px 0;">{nome}</h3>
        <p style="margin:2px 0;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0;">🥚 <b>Repro:</b> {"Ovíparo" if classe != "Mamífero" else "Vivíparo"}</p>
        <p style="margin:2px 0;">🥩 <b>Alimentação:</b> {alim}</p>
        {f'<p style="color:#ffd700; font-weight:bold; margin-top:5px;">{footer_text}</p>' if footer_text else ''}
    </div>"""
    st.markdown(html_cartao, unsafe_allow_html=True)
    
    if show_button:
        # Se estiver no Zoo, mostra botão de excluir. Se não, mostra botão de capturar.
        if is_zoo:
            if st.button(f"🗑️ Excluir", key=f"del_{prefixo}_{idx}", use_container_width=True):
                st.session_state.zoo.pop(idx)
                st.rerun()
        else:
            if st.button("📥 Zoo", key=f"btn_{prefixo}_{idx}_{random.randint(0,999)}", use_container_width=True):
                st.session_state.zoo.append(an)
                st.toast(f"{nome} adicionado!")

# 8. LISTAS
florestas_mundo = ["Amazónia", "Congo", "Taiga Siberiana", "Daintree Austrália", "Floresta Negra", "Mata Atlântica", "Bornéu", "Monteverde Costa Rica", "Tongass Alasca", "Bialowieza Polónia"]
oceanos_mundo = ["Oceano Pacífico", "Oceano Atlântico", "Oceano Índico", "Oceano Ártico", "Oceano Antártico", "Mar Mediterrâneo", "Mar Vermelho", "Mar das Caraíbas", "Mar de Coral", "Mar Morto"]
paises_70 = ["Portugal", "Brasil", "Angola", "Moçambique", "Cabo Verde", "Espanha", "França", "Itália", "Alemanha", "Reino Unido", "EUA", "Canadá", "México", "Argentina", "Chile", "Colômbia", "Peru", "China", "Japão", "Coreia do Sul", "Índia", "Austrália", "Nova Zelândia", "Egito", "África do Sul", "Nigéria", "Quénia", "Marrocos", "Rússia", "Ucrânia", "Polónia", "Suécia", "Noruega", "Finlândia", "Dinamarca", "Holanda", "Bélgica", "Suíça", "Áustria", "Grécia", "Turquia", "Irão", "Iraque", "Arábia Saudita", "EAU", "Tailândia", "Vietname", "Indonésia", "Filipinas", "Malásia", "Singapura", "Paquistão", "Bangladesh", "Israel", "Suíça", "Irlanda", "Islândia", "Cuba", "Jamaica", "Uruguai", "Paraguai", "Bolívia", "Equador", "Venezuela", "Panamá", "Costa Rica", "Guatemala", "Honduras", "Senegal", "Gana"]

# 9. ABAS
if aba == "🌲 Florestas":
    sel = st.selectbox("Escolha uma Floresta:", florestas_mundo)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    ans = r.json().get('results', [])
    for i in range(0, len(ans), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(ans):
                with cols[j]: card(ans[i+j], "floresta", i+j)

elif aba == "🌊 Oceanos":
    sel = st.selectbox("Escolha um Oceano:", oceanos_mundo)
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    ans = r.json().get('results', [])
    for i in range(0, len(ans), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(ans):
                with cols[j]: card(ans[i+j], "oceano", i+j)

elif aba == "🏳️ Países":
    sel = st.selectbox("Escolha um País:", sorted(paises_70))
    r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={sel}&taxon_id=1&per_page=70&locale=pt-PT")
    ans = r.json().get('results', [])
    for i in range(0, len(ans), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(ans):
                with cols[j]: card(ans[i+j], "pais", i+j)

elif aba == "🌀 Salvamento":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1000px-World_map_-_low_resolution.svg.png")
    if st.session_state.id_animal_atual is None:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={random.choice(['Africa','Amazon','Australia'])}&taxon_id=1&per_page=50&locale=pt-PT")
        validos = [a for a in r.json()['results'] if a['id'] not in st.session_state.animais_salvos_ids]
        if validos: st.session_state.id_animal_atual = random.choice(validos)
    if st.session_state.id_animal_atual:
        an = st.session_state.id_animal_atual
        st.warning(f"🆘 ALERTA: Um animal ferido foi localizado!")
        card(an, "resgate", 0, show_button=False)
        if st.button("🚁 ENVIAR HELICÓPTERO"):
            st.markdown('<div class="heli-anim">🚁</div>', unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.pontos_zoologo += 50
            st.session_state.animais_salvos_ids.add(an['id'])
            st.session_state.internados_vet.append({'animal': an, 'data_alta': (datetime.now() + timedelta(hours=24)).timestamp()})
            st.session_state.id_animal_atual = None
            st.rerun()

elif aba == "🏥 Veterinário":
    st.header("🏥 Hospital Veterinário")
    if not st.session_state.internados_vet: st.info("Hospital vazio.")
    else:
        for i in range(0, len(st.session_state.internados_vet), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(st.session_state.internados_vet):
                    item = st.session_state.internados_vet[idx]
                    falta = item['data_alta'] - datetime.now().timestamp()
                    with cols[j]:
                        if falta > 0:
                            h, m = int(falta // 3600), int((falta % 3600) // 60)
                            card(item['animal'], "vet", idx, show_button=False, footer_text=f"⏳ Alta em: {h}h {m}m")
                        else:
                            card(item['animal'], "vet", idx, show_button=False, footer_text="✅ Recuperado!")
                            if st.button("🏁 Enviar para Zoo", key=f"move_{idx}", use_container_width=True):
                                st.session_state.zoo.append(item['animal']); st.session_state.internados_vet.pop(idx); st.rerun()

elif aba == "🔬 Laboratório":
    busca = st.text_input("🔍 Pesquisa:")
    if busca:
        r = requests.get(f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&per_page=70&locale=pt-PT")
        ans = r.json().get('results', [])
        for i in range(0, len(ans), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(ans):
                    with cols[j]: card(ans[i+j], "lab", i+j)

elif aba == "🐾 Meu Zoo":
    st.header("🐾 Meu Zoo")
    if not st.session_state.zoo:
        st.info("O seu Zoo está vazio. Explore ou salve animais!")
    for i in range(0, len(st.session_state.zoo), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(st.session_state.zoo):
                with cols[j]: card(st.session_state.zoo[idx], "zoo", idx, is_zoo=True)

elif aba == "⚙️ Definições":
    st.session_state.c_mega = st.text_input("Código Mega", type="password", value=st.session_state.c_mega)
    st.session_state.c_24h = st.text_input("Código 24h", type="password", value=st.session_state.c_24h)
    st.session_state.brilho = st.slider("Brilho", 50, 150, st.session_state.brilho)
    if st.button("Guardar"): st.rerun()
