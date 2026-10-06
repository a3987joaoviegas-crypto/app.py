import requests
import random
import streamlit as st

st.set_page_config(
    page_title="MundoVivo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071f16 0%, #0b3d2e 50%, #06251b 100%);
    color: white;
}

.hero {
    padding: 2rem;
    border-radius: 25px;
    background: linear-gradient(135deg, #126044, #042b1f);
    margin-bottom: 1.5rem;
}

.animal-card {
    padding: 1.5rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 1.5rem;
}

.tag {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    margin: 0.2rem;
    border-radius: 20px;
    background: rgba(92,184,92,0.2);
}

.safe {
    padding: 1rem;
    border-radius: 15px;
    background: rgba(40,150,90,0.2);
    border-left: 5px solid #5be39b;
}

.danger {
    padding: 1rem;
    border-radius: 15px;
    background: rgba(180,30,30,0.2);
    border-left: 5px solid #ff5c5c;
}

.stats {
    padding: 1rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.08);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# API
# ============================================================

API = "https://api.inaturalist.org/v1"


# ============================================================
# DADOS
# ============================================================

COUNTRIES = {
    "Portugal": 105,
    "Espanha": 143,
    "Brasil": 21,
    "França": 127,
    "Itália": 20,
    "Alemanha": 154,
    "Reino Unido": 826,
    "Estados Unidos": 1,
    "Canadá": 6712,
    "Austrália": 6744,
    "Japão": 8344,
    "África do Sul": 7148,
}

FORESTS = {
    "Amazónia": (-73.9, -18.0, -44.0, 5.0),
    "Floresta Atlântica": (-57.0, -30.0, -38.0, 8.0),
    "Congo": (9.0, -13.0, 31.0, 5.0),
    "Bornéu": (108.0, -4.0, 119.0, 8.0),
    "Taiga Siberiana": (30.0, 50.0, 180.0, 75.0),
}

OCEANS = {
    "Atlântico": (-80.0, -60.0, 20.0, 65.0),
    "Pacífico": (120.0, -60.0, -70.0, 60.0),
    "Índico": (20.0, -40.0, 120.0, 30.0),
    "Ártico": (-180.0, 65.0, 180.0, 90.0),
    "Antártico": (-180.0, -90.0, 180.0, -55.0),
}


COMMON_NAMES = {
    "Trithemis annulata": "Asa Descendente Violeta",
    "Panthera leo": "Leão",
    "Panthera tigris": "Tigre",
    "Canis lupus": "Lobo",
    "Ursus arctos": "Urso-pardo",
    "Elephas maximus": "Elefante-asiático",
    "Loxodonta africana": "Elefante-africano",
    "Delphinus delphis": "Golfinho-comum",
    "Orcinus orca": "Orca",
    "Balaenoptera musculus": "Baleia-azul",
    "Carcharodon carcharias": "Tubarão-branco",
    "Chelonia mydas": "Tartaruga-verde",
    "Aquila chrysaetos": "Águia-real",
    "Bubo bubo": "Bufo-real",
    "Vulpes vulpes": "Raposa-vermelha",
}


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "🏠 Início",
    "favorites": [],
    "rescued": [],
    "veterinary": [],
    "quiz_score": 0,
    "quiz_total": 0,
    "achievements": [],
    "last_animals": [],
    "search_results": [],
    "fusion_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# API
# ============================================================

def api_get(endpoint, params=None):
    try:
        response = requests.get(
            f"{API}/{endpoint}",
            params=params or {},
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


# ============================================================
# INFORMAÇÕES DOS ANIMAIS
# ============================================================

def safe_photo(animal):
    photo = animal.get("default_photo")

    if not photo:
        photo = animal.get("taxon", {}).get("default_photo")

    if isinstance(photo, dict):
        return (
            photo.get("medium_url")
            or photo.get("square_url")
            or photo.get("original_url")
        )

    return None


def animal_name(animal):
    scientific = animal.get("name", "Animal desconhecido")

    return (
        animal.get("preferred_common_name")
        or COMMON_NAMES.get(scientific)
        or scientific.replace("_", " ").title()
    )


def class_name(animal):
    iconic = animal.get("iconic_taxon_name")

    if iconic:
        translations = {
            "Insecta": "Inseto",
            "Aves": "Ave",
            "Mammalia": "Mamífero",
            "Reptilia": "Réptil",
            "Amphibia": "Anfíbio",
            "Actinopterygii": "Peixe",
            "Arachnida": "Aracnídeo",
            "Mollusca": "Molusco",
            "Plantae": "Planta",
        }

        return translations.get(iconic, iconic)

    return "Não disponível"


def get_conservation(animal):
    status = animal.get("conservation_status")

    if isinstance(status, dict):
        return (
            status.get("status_name")
            or status.get("authority")
            or "Não disponível"
        )

    if isinstance(status, list) and status:
        return status[0].get("status_name", "Não disponível")

    return "Não disponível"


def get_diet(animal):
    return animal.get(
        "diet",
        "Néctar, folhas, sementes, frutos, madeira ou outros pequenos organismos, conforme a espécie."
    )


def get_reproduction(animal):
    return animal.get(
        "reproduction",
        "Reprodução sexuada e desenvolvimento através de ovos."
    )


def get_habitat(animal):
    return animal.get(
        "habitat",
        "Florestas, campos, jardins, zonas húmidas, desertos e outros ambientes terrestres."
    )


def get_distribution(animal):
    return animal.get(
        "distribution",
        "Distribuição geográfica disponível nas fontes científicas associadas à espécie."
    )


def get_fun_fact(animal):
    iconic = animal.get("iconic_taxon_name")

    facts = {
        "Insecta":
            "Os insetos constituem um dos grupos de animais mais diversos do planeta.",

        "Aves":
            "As aves possuem adaptações extraordinárias que lhes permitem viver em praticamente todos os ambientes.",

        "Mammalia":
            "Os mamíferos distinguem-se, entre outras características, pela presença de glândulas mamárias.",

        "Reptilia":
            "Os répteis possuem adaptações que lhes permitem sobreviver em ambientes terrestres muito variados.",

        "Amphibia":
            "Os anfíbios são excelentes indicadores da saúde dos ecossistemas.",

        "Actinopterygii":
            "Os peixes de barbatanas raiadas representam a maioria das espécies de peixes existentes.",

        "Arachnida":
            "Os aracnídeos incluem animais como aranhas, escorpiões e carraças."
    }

    return facts.get(
        iconic,
        "A natureza está cheia de adaptações e características extraordinárias."
    )


# ============================================================
# PESQUISA
# ============================================================

def normalize_taxa(results):
    output = []

    for item in results:
        taxon = item.get("taxon", item)

        if taxon and taxon.get("name"):
            output.append(taxon)

    return output


def search_animals(query):
    data = api_get(
        "taxa",
        {
            "q": query,
            "rank": "species",
            "per_page": 30
        }
    )

    results = normalize_taxa(data.get("results", []))

    st.session_state.search_results = results
    st.session_state.last_animals = results

    return results


def observations_bbox(bbox):
    swlng, swlat, nelng, nelat = bbox

    data = api_get(
        "observations",
        {
            "swlng": swlng,
            "swlat": swlat,
            "nelng": nelng,
            "nelat": nelat,
            "per_page": 40,
            "quality_grade": "research",
            "order": "desc",
            "order_by": "observed_on"
        }
    )

    taxa = []
    seen = set()

    for observation in data.get("results", []):
        taxon = observation.get("taxon")

        if taxon and taxon.get("id") not in seen:
            seen.add(taxon.get("id"))
            taxa.append(taxon)

    st.session_state.last_animals = taxa

    return taxa


def country_animals(country):
    place_id = COUNTRIES.get(country)

    if not place_id:
        return []

    data = api_get(
        "observations",
        {
            "place_id": place_id,
            "per_page": 40,
            "quality_grade": "research",
            "order": "desc",
            "order_by": "observed_on"
        }
    )

    taxa = []
    seen = set()

    for observation in data.get("results", []):
        taxon = observation.get("taxon")

        if taxon and taxon.get("id") not in seen:
            seen.add(taxon.get("id"))
            taxa.append(taxon)

    st.session_state.last_animals = taxa

    return taxa


# ============================================================
# FAVORITOS / RESGATE / VETERINÁRIO
# ============================================================

def add_favorite(animal):
    name = animal_name(animal)

    if name not in [
        animal_name(x)
        for x in st.session_state.favorites
    ]:
        st.session_state.favorites.append(animal)


def remove_favorite(name):
    st.session_state.favorites = [
        animal
        for animal in st.session_state.favorites
        if animal_name(animal) != name
    ]


def add_rescue(animal):
    if animal not in st.session_state.rescued:
        st.session_state.rescued.append(animal)

    st.success("🚑 Animal adicionado ao salvamento.")


def open_vet(animal):
    if animal not in st.session_state.veterinary:
        st.session_state.veterinary.append(animal)

    st.success("🩺 Animal enviado para a área veterinária.")


# ============================================================
# CARTÃO DE CIDADÃO
# ============================================================

def show_animal_card(animal):
    name = animal_name(animal)
    scientific = animal.get("name", "Não disponível")
    taxon_id = animal.get("id", "Não disponível")
    conservation = get_conservation(animal)

    st.markdown(
        '<div class="animal-card">',
        unsafe_allow_html=True
    )

    photo = safe_photo(animal)

    if photo:
        st.image(photo, use_container_width=True)

    st.markdown("## 🪪 CARTÃO DE CIDADÃO DO ANIMAL")

    st.markdown(f"### 🐾 {name}")

    st.markdown("### 🆔 Identificação")

    st.markdown(f"""
**Nome comum:** {name}

**Nome científico:** *{scientific}*

**Classe:** {class_name(animal)}

**Reino:** Animalia

**ID científico:** {taxon_id}

**Estado de conservação:** {conservation}
""")

    st.markdown("### 🔬 Características")

    st.markdown(f"""
🍖 **Alimentação:** {get_diet(animal)}

🥚 **Reprodução:** {get_reproduction(animal)}

🌍 **Habitat:** {get_habitat(animal)}

🗺️ **Distribuição:** {get_distribution(animal)}
""")

    st.markdown("### 💡 Sabias que...")

    st.info(get_fun_fact(animal))

    st.markdown(
        f"🛡️ **Estado de conservação:** {conservation}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if name in [
            animal_name(x)
            for x in st.session_state.favorites
        ]:
            if st.button(
                "💔 Remover dos favoritos",
                key=f"remove_{taxon_id}"
            ):
                remove_favorite(name)
                st.rerun()
        else:
            if st.button(
                "❤️ Favorito",
                key=f"fav_{taxon_id}"
            ):
                add_favorite(animal)
                st.rerun()

    with col2:
        if st.button(
            "🚑 Resgate",
            key=f"rescue_{taxon_id}"
        ):
            add_rescue(animal)

    with col3:
        if st.button(
            "🩺 Veterinário",
            key=f"vet_{taxon_id}"
        ):
            open_vet(animal)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# ENCICLOPÉDIA
# ============================================================

def show_encyclopedia(animal):
    name = animal_name(animal)
    scientific = animal.get("name", "Não disponível")
    taxon_id = animal.get("id", "Não disponível")
    conservation = get_conservation(animal)

    st.markdown(
        '<div class="animal-card">',
        unsafe_allow_html=True
    )

    photo = safe_photo(animal)

    if photo:
        st.image(photo, use_container_width=True)

    st.markdown("## 📚 ENCICLOPÉDIA")

    st.markdown(f"### 🐾 {name}")

    st.markdown("### 🆔 Identificação")

    st.markdown(f"""
**Nome comum:** {name}

**Nome científico:** *{scientific}*

**Classe:** {class_name(animal)}

**Reino:** Animalia

**ID científico:** {taxon_id}

**Estado de conservação:** {conservation}
""")

    st.markdown("---")

    st.markdown("### 🔬 Características")

    st.markdown(f"""
🍖 **Alimentação:** {get_diet(animal)}

🥚 **Reprodução:** {get_reproduction(animal)}

🌍 **Habitat:** {get_habitat(animal)}

🗺️ **Distribuição:** {get_distribution(animal)}
""")

    st.markdown("---")

    st.markdown("### 💡 Sabias que...")

    st.info(get_fun_fact(animal))

    st.markdown("---")

    if conservation == "Não disponível":
        st.markdown(
            '<div class="safe">🛡️ <b>Estado de conservação:</b> Não disponível</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="safe">🛡️ <b>Estado de conservação:</b> {conservation}</div>',
            unsafe_allow_html=True
        )

    st.markdown("### ⚡ Ações")

    col1, col2, col3 = st.columns(3)

    with col1:
        if name in [
            animal_name(x)
            for x in st.session_state.favorites
        ]:
            if st.button(
                "💔 Remover dos favoritos",
                key=f"ency_remove_{taxon_id}"
            ):
                remove_favorite(name)
                st.rerun()
        else:
            if st.button(
                "❤️ Adicionar aos favoritos",
                key=f"ency_fav_{taxon_id}"
            ):
                add_favorite(animal)
                st.rerun()

    with col2:
        if st.button(
            "🚑 Resgatar animal",
            key=f"ency_rescue_{taxon_id}"
        ):
            add_rescue(animal)

    with col3:
        if st.button(
            "🩺 Veterinário",
            key=f"ency_vet_{taxon_id}"
        ):
            open_vet(animal)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RESULTADOS
# ============================================================

def show_results(results):
    if not results:
        st.warning("😕 Não foram encontrados animais.")
        return

    for animal in results:
        show_animal_card(animal)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 🌍 MundoVivo")

    st.caption("Explora o mundo animal")

    pages = [
        "🏠 Início",
        "❤️ Meu Zoo",
        "🌳 Florestas",
        "🌊 Oceanos",
        "🌍 Países",
        "🔬 Laboratório",
        "📚 Enciclopédia",
        "📸 Visão IA",
        "🚑 Salvamento",
        "🩺 Veterinário",
        "🧬 Tanque de Fusão",
        "🧠 Quiz",
        "🏆 Conquistas",
        "📊 Estatísticas",
        "⚙️ Definições"
    ]

    page = st.radio(
        "Menu",
        pages,
        index=pages.index(st.session_state.page)
    )

    st.session_state.page = page


# ============================================================
# INÍCIO
# ============================================================

if page == "🏠 Início":

    st.markdown("""
    <div class="hero">
        <h1>🌍 MundoVivo</h1>
        <p>Explora animais, habitats e a biodiversidade do nosso planeta.</p>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input(
        "🔎 Procurar um animal",
        placeholder="Ex.: leão, lobo, Trithemis annulata..."
    )

    if query:
        results = search_animals(query)
        show_results(results)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="stats"><h2>🐾</h2><p>Animais</p></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="stats"><h2>🌳</h2><p>Habitats</p></div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="stats"><h2>📚</h2><p>Enciclopédia</p></div>',
            unsafe_allow_html=True
        )


# ============================================================
# MEU ZOO
# ============================================================

elif page == "❤️ Meu Zoo":

    st.title("❤️ Meu Zoo")

    if not st.session_state.favorites:
        st.info("Ainda não tens animais favoritos.")
    else:
        for animal in st.session_state.favorites:
            show_animal_card(animal)


# ============================================================
# FLORESTAS
# ============================================================

elif page == "🌳 Florestas":

    st.title("🌳 Florestas")

    forest = st.selectbox(
        "Escolhe uma floresta",
        list(FORESTS.keys())
    )

    if st.button("🔎 Explorar floresta"):
        results = observations_bbox(FORESTS[forest])
        show_results(results)


# ============================================================
# OCEANOS
# ============================================================

elif page == "🌊 Oceanos":

    st.title("🌊 Oceanos")

    ocean = st.selectbox(
        "Escolhe um oceano",
        list(OCEANS.keys())
    )

    if st.button("🔎 Explorar oceano"):
        results = observations_bbox(OCEANS[ocean])
        show_results(results)


# ============================================================
# PAÍSES
# ============================================================

elif page == "🌍 Países":

    st.title("🌍 Animais por país")

    country = st.selectbox(
        "Escolhe um país",
        list(COUNTRIES.keys())
    )

    if st.button("🔎 Explorar país"):
        results = country_animals(country)
        show_results(results)


# ============================================================
# LABORATÓRIO
# ============================================================

elif page == "🔬 Laboratório":

    st.title("🔬 Laboratório")

    st.write(
        "Pesquisa espécies e explora informações científicas."
    )

    query = st.text_input(
        "🔬 Procurar espécie",
        placeholder="Ex.: Trithemis annulata"
    )

    if query:
        results = search_animals(query)
        show_results(results)


# ============================================================
# ENCICLOPÉDIA
# ============================================================

elif page == "📚 Enciclopédia":

    st.title("📚 Enciclopédia Animal")

    st.write(
        "Consulta o cartão de cidadão completo de qualquer animal."
    )

    query = st.text_input(
        "🔎 Procurar animal",
        placeholder="Ex.: Asa Descendente Violeta, leão, lobo..."
    )

    if query:

        results = search_animals(query)

        if results:

            selected = st.selectbox(
                "🐾 Escolhe o animal",
                results,
                format_func=animal_name
            )

            if selected:
                show_encyclopedia(selected)

        else:

            st.warning(
                "😕 Não encontrei esse animal."
            )

    elif st.session_state.last_animals:

        st.markdown("### 🐾 Animais recentes")

        selected = st.selectbox(
            "Escolhe um animal",
            st.session_state.last_animals,
            format_func=animal_name
        )

        if selected:
            show_encyclopedia(selected)

    else:

        st.info(
            "🔎 Procura um animal para abrir a sua ficha completa."
        )


# ============================================================
# VISÃO IA
# ============================================================

elif page == "📸 Visão IA":

    st.title("📸 Visão IA")

    st.write(
        "Envia uma fotografia para explorar um animal."
    )

    uploaded = st.file_uploader(
        "📷 Escolhe uma fotografia",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded:
        st.image(
            uploaded,
            caption="Imagem selecionada",
            use_container_width=True
        )

        st.info(
            "A identificação automática por IA pode ser adicionada nesta área."
        )


# ============================================================
# SALVAMENTO
# ============================================================

elif page == "🚑 Salvamento":

    st.title("🚑 Salvamento")

    if not st.session_state.rescued:

        st.info(
            "Não tens animais registados para salvamento."
        )

    else:

        for animal in st.session_state.rescued:
            show_animal_card(animal)


# ============================================================
# VETERINÁRIO
# ============================================================

elif page == "🩺 Veterinário":

    st.title("🩺 Veterinário")

    if not st.session_state.veterinary:

        st.info(
            "Não existem animais nesta área."
        )

    else:

        for animal in st.session_state.veterinary:
            show_animal_card(animal)


# ============================================================
# TANQUE DE FUSÃO
# ============================================================

elif page == "🧬 Tanque de Fusão":

    st.title("🧬 Tanque de Fusão")

    st.write(
        "Combina dois animais para criar uma fusão imaginária."
    )

    animals = st.session_state.last_animals

    if len(animals) >= 2:

        col1, col2 = st.columns(2)

        with col1:

            animal1 = st.selectbox(
                "🐾 Primeiro animal",
                animals,
                format_func=animal_name
            )

        with col2:

            animal2 = st.selectbox(
                "🐾 Segundo animal",
                animals,
                format_func=animal_name,
                key="animal2"
            )

        if st.button("🧬 Fundir animais"):

            result = (
                f"{animal_name(animal1)} + "
                f"{animal_name(animal2)}"
            )

            st.session_state.fusion_result = result

            st.success(
                f"🧬 Criaste: {result}"
            )

    else:

        st.info(
            "Pesquisa alguns animais primeiro para usar o Tanque de Fusão."
        )


# ============================================================
# QUIZ
# ============================================================

elif page == "🧠 Quiz":

    st.title("🧠 Quiz Animal")

    animals = st.session_state.last_animals

    if len(animals) < 4:

        st.info(
            "Pesquisa pelo menos alguns animais antes de iniciar o quiz."
        )

    else:

        animal = random.choice(animals)

        photo = safe_photo(animal)

        if photo:
            st.image(
                photo,
                use_container_width=True
            )

        correct = animal_name(animal)

        options = [correct]

        while len(options) < 4:

            option = animal_name(
                random.choice(animals)
            )

            if option not in options:
                options.append(option)

        random.shuffle(options)

        answer = st.radio(
            "🐾 Que animal é este?",
            options
        )

        if st.button("✅ Responder"):

            st.session_state.quiz_total += 1

            if answer == correct:

                st.session_state.quiz_score += 1

                st.success(
                    "🎉 Resposta certa!"
                )

            else:

                st.error(
                    f"❌ A resposta certa era {correct}."
                )

        st.write(
            f"Pontuação: "
            f"**{st.session_state.quiz_score} / "
            f"{st.session_state.quiz_total}**"
        )


# ============================================================
# CONQUISTAS
# ============================================================

elif page == "🏆 Conquistas":

    st.title("🏆 Conquistas")

    achievements = []

    if st.session_state.favorites:
        achievements.append(
            "❤️ Primeiro animal favorito"
        )

    if len(st.session_state.favorites) >= 5:
        achievements.append(
            "🐾 Colecionador de animais"
        )

    if st.session_state.quiz_score >= 5:
        achievements.append(
            "🧠 Mestre do Quiz"
        )

    if st.session_state.rescued:
        achievements.append(
            "🚑 Herói do salvamento"
        )

    if not achievements:

        st.info(
            "Ainda não desbloqueaste conquistas."
        )

    else:

        for achievement in achievements:

            st.success(
                f"🏆 {achievement}"
            )


# ============================================================
# ESTATÍSTICAS
# ============================================================

elif page == "📊 Estatísticas":

    st.title("📊 Estatísticas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "❤️ Favoritos",
            len(st.session_state.favorites)
        )

    with col2:
        st.metric(
            "🚑 Resgates",
            len(st.session_state.rescued)
        )

    with col3:
        st.metric(
            "🩺 Veterinário",
            len(st.session_state.veterinary)
        )

    with col4:
        st.metric(
            "🧠 Quiz",
            st.session_state.quiz_score
        )


# ============================================================
# DEFINIÇÕES
# ============================================================

elif page == "⚙️ Definições":

    st.title("⚙️ Definições")

    st.write(
        "Definições do MundoVivo."
    )

    if st.button("🗑️ Limpar favoritos"):

        st.session_state.favorites = []

        st.success(
            "Favoritos limpos."
        )

    if st.button("🔄 Limpar dados da sessão"):

        st.session_state.favorites = []
        st.session_state.rescued = []
        st.session_state.veterinary = []
        st.session_state.achievements = []
        st.session_state.last_animals = []
        st.session_state.search_results = []
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
        st.session_state.fusion_result = None

        st.success(
            "Dados da sessão limpos."
        )
