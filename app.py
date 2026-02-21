def render_cartao(an, local):
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/150")
    nome = an.get('preferred_common_name', an.get('name', 'Espécie')).title()
    classe = an.get('iconic_taxon_name', 'Mamífero')
    
    st.markdown(f"""
    <div class="cartao-cidadao">
        <img src="{foto}" style="width:100%; border-radius:12px; height:150px; object-fit:cover;">
        <h4>{nome}</h4>
        <div style='font-size: 0.8em; text-align: left; opacity: 0.9;'>
            <b>🧬 Classe:</b> {classe}<br>
            <b>🏠 Habitat:</b> Nativo<br>
            <b>🍼 Reprodução:</b> Biológica
        </div>
    """, unsafe_allow_html=True)

    # A ÚNICA PARTE EXCLUSIVA DE INFORMAÇÃO NO CARD
    if st.session_state.premium_ativo and tem_acesso:
        st.markdown("<div style='background: #ffd700; color: black; border-radius: 5px; margin: 5px 0; font-weight: bold; font-size: 0.7em;'>🛡️ CONSERVAÇÃO: PROTEGIDO</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Botões de ação abaixo do card...
    c1, c2 = st.columns(2)
    # ... resto do código dos botões
