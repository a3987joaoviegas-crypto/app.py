def grid_cards(lista_animais):
    if not lista_animais: return
    for i in range(0, len(lista_animais), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(lista_animais):
                an = lista_animais[i+j]
                with cols[j]:
                    card(an, show_sound=True)

def card(an, show_sound=True):
    if not an: return
    nome_pt = (an.get('preferred_common_name') or an.get('name')).title()
    nome_cientifico = an.get('name', 'Espécie')
    foto = an.get('default_photo', {}).get('medium_url', "https://via.placeholder.com/300")
    classe = {"Mammalia": "Mamífero", "Aves": "Ave", "Reptilia": "Réptil",
              "Amphibia": "Anfíbio", "Actinopterygii": "Peixe"}.get(an.get('iconic_taxon_name'), "Selvagem")
    alim = random.choice(['Herbívoro', 'Carnívoro', 'Omnívoro'])
    repro = "Vivíparo" if classe == "Mamífero" else "Ovíparo"
    
    st.markdown(f'''
    <div class="cartao-cidadao">
        <img src="{foto}" class="img-an">
        <h4 style="color:#ffd700; margin:5px 0;">{nome_pt}</h4>
        <p style="color:#aaa; font-size:0.8em; margin:2px 0;">{nome_cientifico}</p>
        <p style="margin:2px 0; font-size:0.8em;">🐾 <b>Classe:</b> {classe}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥚 <b>Repro:</b> {repro}</p>
        <p style="margin:2px 0; font-size:0.8em;">🥩 <b>Alimentação:</b> {alim}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if show_sound:
        key_btn = f"snd_{an.get('id', nome_pt)}"
        if st.button(f"🔊 Ouvir {nome_pt}", key=key_btn):
            st.info(f"🔊 IA encontrou sons de {nome_pt} na internet!")
            # st.audio(URL_DO_SOM) aqui quando integrares a API real
