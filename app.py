import streamlit as st
import requests

# 1. ESTADO DO SISTEMA
if 'zoo' not in st.session_state:
    st.session_state.update({
        'zoo': [], 
        'dna_storage': [], 
        'premium_master': False, # Se o código foi inserido
        'modo_visao': "Normal"    # O que o usuário está vendo no momento
    })

# 2. CSS AVANÇADO
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .card { background: #1a1c23; padding: 20px; border-radius: 15px; border: 1px solid #333; color: white; }
    .premium-info { border: 2px solid #ffd700; background: rgba(255, 215, 0, 0.05); padding: 15px; border-radius: 10px; margin-top: 10px; }
    .lock-text { color: #555; font-style: italic; font-size: 0.8em; }
    .sidebar-premium { background: linear-gradient(180deg, #1a1c23 0%, #2d2301 100%); padding: 10px; border-radius: 10px; border: 1px solid #ffd700; }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR ESPECÍFICA (A LÓGICA QUE PEDISTE)
with st.sidebar:
    st.title("🛡️ CONTROLO VITAL")
    
    # Input do código
    codigo = st.text_input("CHAVE DE ACESSO:", type="password")
    st.session_state.premium_master = (codigo == "6626")

    if st.session_state.premium_master:
        st.markdown('<div class="sidebar-premium">', unsafe_allow_html=True)
        st.success("💎 MODO PREMIUM DESBLOQUEADO")
        
        # O INTERRUPTOR PARA VOLTAR À SIDEBAR NORMAL/VISÃO NORMAL
        st.session_state.modo_visao = st.toggle("ATIVAR INTERFACE PREMIUM", value=True)
        
        if st.session_state.modo_visao:
            st.subheader("🧬 LABORATÓRIO DNA")
            st.write(f"Amostras: {len(st.session_state.dna_storage)}")
            if st.button("🧪 Limpar DNA"): st.session_state.dna_storage = []
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔓 Digite o código para recursos VIP")
        st.session_state.modo_visao = False

    st.divider()
    st.subheader(f"🦁 MEU ZOO ({len(st.session_state.zoo)})")
    for bicho in st.session_state.zoo[-8:]:
        st.caption(f"✓ {bicho}")

# 4. FUNÇÃO DE CARD (ADAPTADA AO INTERRUPTOR)
def render_animal(an):
    nome = an.get('preferred_common_name', an['name']).title()
    foto = an.get('default_photo', {}).get('medium_url', "")
    classe = an.get('iconic_taxon_name', 'Desconhecido')
    
    st.markdown(f"""
    <div class="card">
        <img src="{foto}" width="100%" style="border-radius: 10px; filter: {'sepia(0.5)' if not st.session_state.modo_visao else 'none'};">
        <h3 style="color:#2ecc71;">{nome}</h3>
        <p><b>🧬 Classe:</b> {classe}</p>
        <p><b>🏠 Habitat:</b> Nativo</p>
        <p><b>🍼 Reprodução:</b> Biológica</p>
        <p><b>🍖 Alimentação:</b> Dieta Natural</p>
    """, unsafe_allow_html=True)

    # CONSERVAÇÃO E DNA SÓ APARECEM SE O INTERRUPTOR ESTIVER LIGADO
    if st.session_state.modo_visao:
        st.markdown(f"""
        <div class="premium-info">
            <b style="color: #ffd700;">🛡️ CONSERVAÇÃO:</b> Ameaçada (IUCN)<br>
            <small>Dados protegidos libertados pelo sistema 6626.</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🧬 EXTRAIR DNA", key=f"dna_{an['id']}"):
            st.session_state.dna_storage.append(nome)
            st.toast("🧬 Genoma copiado!")
    else:
        st.markdown('<p class="lock-text">🔒 Status de Conservação e DNA bloqueados.</p>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(f"📥 CAPTURAR {nome}", key=f"cap_{an['id']}"):
        st.session_state.zoo.append(nome)

# 5. CONTEÚDO PRINCIPAL
st.title("🌍 MUNDO VIVO: EXPLORER")
busca = st.text_input("Pesquisar Espécie:", "Lobo")

if busca:
    try:
        res = requests.get(f"https://api.inaturalist.org/v1/taxa?q={busca}&taxon_id=1&per_page=3").json().get('results', [])
        cols = st.columns(3)
        for i, animal in enumerate(res):
            with cols[i]:
                render_animal(animal)
    except:
        st.error("Erro na rede.")

# 6. FUSÃO (SÓ NO MODO PREMIUM ATIVO)
if st.session_state.modo_visao and len(st.session_state.dna_storage) >= 2:
    st.divider()
    st.subheader("🧪 CÂMARA DE FUSÃO HÍBRIDA")
    if st.button("⚡ GERAR HÍBRIDO"):
        novo = st.session_state.dna_storage[-2][:3] + st.session_state.dna_storage[-1][-3:]
        st.warning(f"NOVA ESPÉCIE: {novo.upper()}")
        st.balloons()
