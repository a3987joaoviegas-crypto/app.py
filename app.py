import random
import time
from datetime import datetime
from urllib.parse import quote

import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="MundoVivo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, rgba(0, 100, 70, 0.35), transparent 35%),
        radial-gradient(circle at bottom right, rgba(0, 70, 50, 0.30), transparent 35%),
        linear-gradient(135deg, #071b16 0%, #0b2920 45%, #06130f 100%);
    color: white;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06140f, #0a2119);
}

.hero {
    padding: 30px;
    border-radius: 25px;
    background: linear-gradient(135deg, #0c5c43, #07372a);
    box-shadow: 0 10px 30px rgba(0,0,0,.35);
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 48px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 19px;
    opacity: .9;
}

.animal-card {
    padding: 22px;
    border-radius: 22px;
    background: rgba(10, 40, 30, .92);
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 8px 25px rgba(0,0,0,.28);
    margin-bottom: 22px;
}

.tag {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #174f3b;
    margin: 3px;
    font-size: 13px;
}

.safe {
    padding: 15px;
    border-radius: 15px;
    background: rgba(30, 110, 75, .35);
    border: 1px solid rgba(100, 220, 160, .25);
    margin-top: 10px;
}

.danger {
    padding: 15px;
    border-radius: 15px;
    background: rgba(120, 45, 35, .35);
    border: 1px solid rgba(255, 130, 100, .25);
    margin-top: 10px;
}

.stat-box {
    padding: 20px;
    border-radius: 18px;
    background: rgba(10, 50, 38, .8);
    text-align: center;
}

.small-text {
    font-size: 13px;
    opacity: .75;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# API
# ============================================================

API_BASE = "https://api.inaturalist.org/v1"


# ============================================================
# DADOS
# ============================================================

COUNTRY_IDS = {
    "Portugal": 7122,
    "Brasil": 7196,
    "Espanha": 7239,
    "França": 6753,
    "Itália": 6973,
    "Alemanha": 7191,
    "Reino Unido": 6825,
    "Estados Unidos": 1,
    "Canadá": 6712,
    "Austrália": 6744,
    "Japão": 6907,
    "Índia": 6681,
    "África do Sul": 6857,
    "México": 6811
}


FORESTS = {
    "Amazónia": {
        "swlat": -15,
        "swlng": -75,
        "nelat": 5,
        "nelng": -45
    },
    "Floresta do Congo": {
        "swlat": -13,
        "swlng": 10,
        "nelat": 8,
        "nelng": 32
    },
    "Floresta Negra": {
        "swlat": 47.4,
        "swlng": 7.5,
        "nelat": 49.2,
        "nelng": 9.8
    },
    "Floresta Boreal": {
        "swlat": 48,
        "swlng": -140,
        "nelat": 70,
        "nelng": -60
    },
    "Floresta Tropical do Sudeste Asiático": {
        "swlat": -10,
        "swlng": 95,
        "nelat": 20,
        "nelng": 150
    }
}


OCEANS = {
    "Atlântico": {
        "swlat": -60,
        "swlng": -70,
        "nelat": 60,
        "nelng": 20
    },
    "Pacífico": {
        "swlat": -60,
        "swlng": 120,
        "nelat": 60,
        "nelng": -80
    },
    "Índico": {
        "swlat": -60,
        "swlng": 20,
        "nelat": 30,
        "nelng": 120
    },
    "Ártico": {
        "swlat": 60,
        "swlng": -180,
        "nelat": 90,
        "nelng": 180
    },
    "Antártico": {
        "swlat": -90,
        "swlng": -180,
        "nelat": -55,
        "nelng": 180
    }
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
    "Vulpes vulpes": "Raposa-vermelha"
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
    "fusion_result": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FUNÇÕES API
# ============================================================

def api_get(endpoint, params=None):
    try:
        response = requests.get(
            f"{API_BASE}/{endpoint}",
            params=params,
            timeout=15
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return {}


def safe_photo(animal):
    photos = animal.get("photos", [])

    if photos:
        url = photos[0].get("url")

        if url:
            return url.replace("square", "medium")

    taxon_photos = animal.get("default_photo")

    if taxon_photos:
        return taxon_photos.get("medium") or taxon_photos.get("url")

    return None


def animal_name(animal):
    scientific = animal.get("name", "")

    if scientific in COMMON_NAMES:
        return COMMON_NAMES[scientific]

    common = animal.get("preferred_common_name")

    if common:
        return common

    common = animal.get("common_name")

    if common:
        return common

    return scientific or "Animal desconhecido"


def class_name(animal):
    iconic = animal.get("iconic_taxon_name", "")

    classes = {
        "Aves": "Ave",
        "Mammalia": "Mamífero",
        "Reptilia": "Réptil",
        "Amphibia": "Anfíbio",
        "Actinopterygii": "Peixe",
        "Insecta": "Inseto",
        "Arachnida": "Aracnídeo",
        "Mollusca": "Molusco",
        "Plantae": "Planta"
    }

    return classes.get(iconic, iconic or "Animal")


def get_conservation(animal):
    conservation = animal.get("conservation_status")

    if isinstance(conservation, dict):
        return (
            conservation.get("name")
            or conservation.get("status_name")
            or "Não disponível"
        )

    if isinstance(conservation, str):
        return conservation

    return "Não disponível"


def get_diet(animal):
    cls = class_name(animal)

    if cls == "Mamífero":
        return "Pode incluir plantas, frutos, sementes, insetos ou outros animais, conforme a espécie."

    if cls == "Ave":
        return "Pode incluir sementes, frutos, insetos, néctar ou pequenos animais, conforme a espécie."

    if cls == "Réptil":
        return "Pode incluir insetos, pequenos animais, frutos ou vegetação, conforme a espécie."

    if cls == "Anfíbio":
        return "Muitos anfíbios alimentam-se de pequenos insetos e outros invertebrados."

    if cls == "Peixe":
        return "A alimentação varia entre algas, pequenos organismos, crustáceos e outros animais."

    if cls == "Inseto":
        return "Pode incluir néctar, folhas, sementes, frutos, madeira ou outros pequenos organismos."

    return "A alimentação varia conforme a espécie."


def get_reproduction(animal):
    cls = class_name(animal)

    if cls in ["Mamífero", "Ave", "Réptil", "Anfíbio", "Peixe"]:
        return "Reprodução sexuada e desenvolvimento através de ovos ou nascimento de crias, conforme a espécie."

    return "Reprodução sexuada e desenvolvimento através de ovos."


def get_habitat(animal):
    cls = class_name(animal)

    if cls == "Mamífero":
        return "Florestas, savanas, montanhas, desertos, zonas costeiras e outros ambientes."

    if cls == "Ave":
        return "Florestas, campos, zonas húmidas, montanhas, cidades e ambientes costeiros."

    if cls == "Réptil":
        return "Florestas, desertos, zonas húmidas, rios, oceanos e outros ambientes."

    if cls == "Peixe":
        return "Rios, lagos, zonas costeiras, recifes e ambientes oceânicos."

    if cls == "Inseto":
        return "Florestas, campos, jardins, zonas húmidas, desertos e outros ambientes terrestres."

    return "Diversos ambientes terrestres ou aquáticos."


def get_distribution(animal):
    place = animal.get("preferred_establishment_means")

    if place:
        return str(place)

    return "Distribuição geográfica disponível nas fontes científicas associadas à espécie."


def get_fun_fact(animal):
    cls = class_name(animal)

    facts = {
        "Mamífero": "Os mamíferos distinguem-se, entre outras características, pela presença de pelos e pela alimentação das crias através de leite.",
        "Ave": "As aves possuem penas e muitas espécies conseguem voar, embora existam também aves que não voam.",
        "Réptil": "Os répteis são vertebrados adaptados a diferentes ambientes terrestres e aquáticos.",
        "Anfíbio": "Muitos anfíbios passam parte do seu ciclo de vida na água e parte em terra.",
        "Peixe": "Os peixes representam um dos grupos de vertebrados mais diversos do planeta.",
        "Inseto": "Os insetos constituem um dos grupos de animais mais diversos do planeta.",
        "Aracnídeo": "Os aracnídeos incluem aranhas, escorpiões, ácaros e carraças.",
        "Molusco": "Os moluscos incluem animais muito diferentes entre si, como caracóis, mexilhões, lulas e polvos."
    }

    return facts.get(
        cls,
        "A biodiversidade do planeta inclui milhões de espécies com características únicas."
    )


# ============================================================
# FILTRO DE ANIMAIS
# ============================================================

def is_plant(animal):
    kingdom = str(animal.get("kingdom_name", "")).lower()
    iconic = str(animal.get("iconic_taxon_name", "")).lower()

    return (
        kingdom == "plantae"
        or iconic == "plantae"
        or "plant" in kingdom
        or "plant" in iconic
    )


def is_animal(animal):
    return not is_plant(animal)


def only_animals(animals):
    return [
        animal
        for animal in animals
        if is_animal(animal)
    ]


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalize_taxa(results):
    normalized = []

    for animal in results:

        if not isinstance(animal, dict):
            continue

        if is_plant(animal):
            continue

        normalized.append(animal)

    return normalized


# ============================================================
# PESQUISA
# ============================================================

def search_animals(query):

    data = api_get(
        "taxa",
        {
            "q": query,
            "rank": "species",
            "per_page": 50
        }
    )

    results = normalize_taxa(
        data.get("results", [])
    )

    st.session_state.search_results = results
    st.session_state.last_animals = results

    return results


# ============================================================
# OBSERVAÇÕES
# ============================================================

def observations_bbox(bbox):

    params = {
        "swlat": bbox["swlat"],
        "swlng": bbox["swlng"],
        "nelat": bbox["nelat"],
        "nelng": bbox["nelng"],
        "per_page": 50,
        "quality_grade": "research"
    }

    data = api_get(
        "observations",
        params
    )

    animals = []

    for observation in data.get("results", []):

        taxon = observation.get("taxon")

        if not taxon:
            continue

        if not is_animal(taxon):
            continue

        animals.append(taxon)

    unique = {}

    for animal in animals:
        animal_id = animal.get("id")

        if animal_id:
            unique[animal_id] = animal

    return list(unique.values())


def country_place_id(country):
    return COUNTRY_IDS.get(country)


def country_animals(country):

    place_id = country_place_id(country)

    if not place_id:
        return []

    data = api_get(
        "observations",
        {
            "place_id": place_id,
            "per_page": 50,
            "quality_grade": "research"
        }
    )

    animals = []

    for observation in data.get("results", []):

        taxon = observation.get("taxon")

        if not taxon:
            continue

        if not is_animal(taxon):
            continue

        animals.append(taxon)

    unique = {}

    for animal in animals:
        animal_id = animal.get("id")

        if animal_id:
            unique[animal_id] = animal

    return list(unique.values())


# ============================================================
# FAVORITOS
# ============================================================

def add_favorite(animal):

    name = animal_name(animal)

    existing = [
        animal_name(x)
        for x in st.session_state.favorites
    ]

    if name not in existing:
        st.session_state.favorites.append(animal)


def remove_favorite(name):

    st.session_state.favorites = [
        animal
        for animal in st.session_state.favorites
        if animal_name(animal) != name
    ]


# ============================================================
# RESGATE
# ============================================================

def add_rescue(animal):

    name = animal_name(animal)

    existing = [
        animal_name(x)
        for x in st.session_state.rescued
    ]

    if name not in existing:
        st.session_state.rescued.append(animal)

    st.success(f"🚑 {name} foi adicionado à lista de resgate.")


# ============================================================
# VETERINÁRIO
# ============================================================

def open_vet(animal):

    name = animal_name(animal)

    if name not in st.session_state.veterinary:
        st.session_state.veterinary.append(name)

    st.success(
        f"🩺 Consulta veterinária preparada para {name}."
    )


# ============================================================
# CARTÃO SIMPLES
# ============================================================

def show_animal_card(animal):

    name = animal_name(animal)
    scientific = animal.get(
        "name",
        "Não disponível"
    )

    taxon_id = animal.get(
        "id",
        "animal"
    )

    conservation = get_conservation(animal)

    st.markdown(
        '<div class="animal-card">',
        unsafe_allow_html=True
    )

    photo = safe_photo(animal)

    if photo:
        st.image(
            photo,
            width=280
        )

    st.markdown(
        f"## 🐾 {name}"
    )

    st.markdown(
        f"""
        <span class="tag">🔬 {scientific}</span>
        <span class="tag">🧬 {class_name(animal)}</span>
        """,
        unsafe_allow_html=True
    )

    if conservation != "Não disponível":
        st.markdown(
            f"""
            <div class="safe">
            🛡️ <b>Estado de conservação:</b>
            {conservation}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        if name in [
            animal_name(x)
            for x in st.session_state.favorites
        ]:

            if st.button(
                "💔 Remover",
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
            "🚑 Resgatar",
            key=f"rescue_{taxon_id}"
        ):
            add_rescue(animal)

    with col3:

        if st.button(
            "🩺 Veterinário",
            key=f"vet_{taxon_id}"
        ):
            open_vet(animal)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# RESULTADOS
# ============================================================

def show_results(results):

    results = only_animals(results)

    if not results:
        st.info(
            "🔎 Não foram encontrados animais."
        )
        return

    st.markdown(
        f"### 🐾 {len(results)} animais encontrados"
    )

    for animal in results:
        show_animal_card(animal)


# ============================================================
# ENCICLOPÉDIA — CARTÃO COMPLETO
# ============================================================

def show_encyclopedia(animal):

    name = animal_name(animal)

    scientific = animal.get(
        "name",
        "Não disponível"
    )

    taxon_id = animal.get(
        "id",
        "Não disponível"
    )

    conservation = get_conservation(animal)

    st.markdown(
        '<div class="animal-card">',
        unsafe_allow_html=True
    )

    photo = safe_photo(animal)

    if photo:
        st.image(
            photo,
            width=280
        )

    st.markdown(
        "## 📚 ENCICLOPÉDIA"
    )

    st.markdown(
        f"### 🐾 {name}"
    )

    st.markdown(
        "### 🆔 Identificação"
    )

    st.markdown(
        f"""
**Nome comum:** {name}

**Nome científico:** *{scientific}*

**Classe:** {class_name(animal)}

**Reino:** Animalia

**ID científico:** {taxon_id}

**Estado de conservação:** {conservation}
"""
    )

    st.markdown("---")

    st.markdown(
        "### 🔬 Características"
    )

    st.markdown(
        f"""
🍖 **Alimentação:** {get_diet(animal)}

🥚 **Reprodução:** {get_reproduction(animal)}

🌍 **Habitat:** {get_habitat(animal)}

🗺️ **Distribuição:** {get_distribution(animal)}
"""
    )

    st.markdown("---")

    st.markdown(
        "### 💡 Sabias que..."
    )

    st.info(
        get_fun_fact(animal)
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div class="safe">
        🛡️ <b>Estado de conservação:</b>
        {conservation}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### ⚡ Ações"
    )

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

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "# 🌍 MundoVivo"
)

st.sidebar.caption(
    "Explora, aprende e protege a vida selvagem."
)

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

st.session_state.page = st.sidebar.radio(
    "Navegação",
    pages,
    index=pages.index(st.session_state.page)
)


# ============================================================
# INÍCIO
# ============================================================

if st.session_state.page == "🏠 Início":

    st.markdown(
        """
        <div class="hero">

        <h1>🌍 MundoVivo</h1>

        <p>
        Explora o mundo animal, descobre espécies,
        aprende sobre a biodiversidade e ajuda a proteger
        o planeta.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "## 🔎 Procurar um animal"
    )

    query = st.text_input(
        "Escreve o nome de um animal",
        placeholder="Ex.: leão, tigre, golfinho..."
    )

    if st.button(
        "🔍 Pesquisar",
        use_container_width=True
    ):

        if query.strip():

            with st.spinner(
                "A procurar animais..."
            ):

                results = search_animals(
                    query.strip()
                )

            show_results(results)

    st.markdown("---")

    st.markdown(
        "## 🐾 Explora o MundoVivo"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 🌳 Florestas

            Descobre os animais que vivem
            nas grandes florestas do planeta.
            """
        )

    with col2:
        st.markdown(
            """
            ### 🌊 Oceanos

            Explora a vida selvagem dos
            grandes oceanos.
            """
        )

    with col3:
        st.markdown(
            """
            ### 📚 Enciclopédia

            Consulta o cartão científico
            completo de cada animal.
            """
        )


# ============================================================
# MEU ZOO
# ============================================================

elif st.session_state.page == "❤️ Meu Zoo":

    st.title(
        "❤️ Meu Zoo"
    )

    if not st.session_state.favorites:

        st.info(
            "Ainda não tens animais favoritos."
        )

    else:

        st.markdown(
            f"### 🐾 {len(st.session_state.favorites)} favoritos"
        )

        for animal in st.session_state.favorites:

            if is_animal(animal):
                show_animal_card(animal)


# ============================================================
# FLORESTAS
# ============================================================

elif st.session_state.page == "🌳 Florestas":

    st.title(
        "🌳 Florestas"
    )

    forest = st.selectbox(
        "Escolhe uma floresta",
        list(FORESTS.keys())
    )

    if st.button(
        "🔎 Explorar floresta",
        use_container_width=True
    ):

        with st.spinner(
            "A procurar animais..."
        ):

            results = only_animals(
                observations_bbox(
                    FORESTS[forest]
                )
            )

        st.session_state.last_animals = results

        show_results(results)


# ============================================================
# OCEANOS
# ============================================================

elif st.session_state.page == "🌊 Oceanos":

    st.title(
        "🌊 Oceanos"
    )

    ocean = st.selectbox(
        "Escolhe um oceano",
        list(OCEANS.keys())
    )

    if st.button(
        "🔎 Explorar oceano",
        use_container_width=True
    ):

        with st.spinner(
            "A procurar animais..."
        ):

            results = only_animals(
                observations_bbox(
                    OCEANS[ocean]
                )
            )

        st.session_state.last_animals = results

        show_results(results)


# ============================================================
# PAÍSES
# ============================================================

elif st.session_state.page == "🌍 Países":

    st.title(
        "🌍 Países"
    )

    country = st.selectbox(
        "Escolhe um país",
        list(COUNTRY_IDS.keys())
    )

    if st.button(
        "🔎 Explorar país",
        use_container_width=True
    ):

        with st.spinner(
            "A procurar animais..."
        ):

            results = only_animals(
                country_animals(country)
            )

        st.session_state.last_animals = results

        show_results(results)


# ============================================================
# LABORATÓRIO
# ============================================================

elif st.session_state.page == "🔬 Laboratório":

    st.title(
        "🔬 Laboratório"
    )

    st.markdown(
        """
        Experimenta com animais e descobre
        informações científicas sobre cada espécie.
        """
    )

    query = st.text_input(
        "🔎 Procurar espécie",
        placeholder="Ex.: Panthera leo"
    )

    if st.button(
        "🧪 Analisar",
        use_container_width=True
    ):

        if query.strip():

            results = search_animals(
                query.strip()
            )

            if results:

                animal = results[0]

                st.success(
                    f"Espécie encontrada: {animal_name(animal)}"
                )

                show_animal_card(animal)

            else:

                st.warning(
                    "Não foi encontrada nenhuma espécie animal."
                )


# ============================================================
# ENCICLOPÉDIA
# ============================================================

elif st.session_state.page == "📚 Enciclopédia":

    st.title(
        "📚 Enciclopédia"
    )

    st.markdown(
        """
        Pesquisa um animal para consultar
        o seu cartão científico completo.
        """
    )

    query = st.text_input(
        "🔎 Procurar animal",
        placeholder="Ex.: leão, elefante, orca..."
    )

    if st.button(
        "📚 Abrir enciclopédia",
        use_container_width=True
    ):

        if query.strip():

            with st.spinner(
                "A procurar na enciclopédia..."
            ):

                results = search_animals(
                    query.strip()
                )

            if results:

                for animal in results[:5]:
                    show_encyclopedia(animal)

            else:

                st.warning(
                    "Não foi encontrado nenhum animal."
                )


# ============================================================
# VISÃO IA
# ============================================================

elif st.session_state.page == "📸 Visão IA":

    st.title(
        "📸 Visão IA"
    )

    st.markdown(
        """
        Carrega uma fotografia de um animal
        para simular uma identificação.
        """
    )

    uploaded = st.file_uploader(
        "📷 Escolhe uma fotografia",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded:

        st.image(
            uploaded,
            width=400
        )

        st.info(
            "🤖 A Visão IA está preparada para analisar a imagem."
        )

        if st.button(
            "🧠 Identificar animal",
            use_container_width=True
        ):

            st.success(
                "🔬 Identificação simulada concluída. "
                "Para uma identificação real, é necessária "
                "uma ligação a um modelo de visão."
            )


# ============================================================
# SALVAMENTO
# ============================================================

elif st.session_state.page == "🚑 Salvamento":

    st.title(
        "🚑 Salvamento"
    )

    st.markdown(
        """
        Aqui podes acompanhar os animais
        que marcaste para resgate.
        """
    )

    if not st.session_state.rescued:

        st.info(
            "Ainda não tens animais na lista de resgate."
        )

    else:

        for animal in st.session_state.rescued:

            if is_animal(animal):

                show_animal_card(animal)


# ============================================================
# VETERINÁRIO
# ============================================================

elif st.session_state.page == "🩺 Veterinário":

    st.title(
        "🩺 Veterinário"
    )

    st.markdown(
        """
        Consulta os animais para os quais
        preparaste uma consulta veterinária.
        """
    )

    if not st.session_state.veterinary:

        st.info(
            "Ainda não existem consultas preparadas."
        )

    else:

        for animal in st.session_state.veterinary:

            st.markdown(
                f"### 🐾 {animal}"
            )

            st.success(
                "🩺 Consulta veterinária registada."
            )


# ============================================================
# TANQUE DE FUSÃO
# ============================================================

elif st.session_state.page == "🧬 Tanque de Fusão":

    st.title(
        "🧬 Tanque de Fusão"
    )

    st.markdown(
        """
        Escolhe dois animais e cria uma
        combinação fictícia.
        """
    )

    animals = only_animals(
        st.session_state.last_animals
        + st.session_state.favorites
    )

    unique = {}

    for animal in animals:

        animal_id = animal.get("id")

        if animal_id:
            unique[animal_id] = animal

    animals = list(unique.values())

    if len(animals) < 2:

        st.info(
            "Pesquisa pelo menos dois animais primeiro."
        )

    else:

        names = [
            animal_name(x)
            for x in animals
        ]

        col1, col2 = st.columns(2)

        with col1:

            first_name = st.selectbox(
                "🐾 Primeiro animal",
                names,
                key="fusion_first"
            )

        with col2:

            second_name = st.selectbox(
                "🐾 Segundo animal",
                names,
                key="fusion_second"
            )

        if st.button(
            "🧬 Fundir animais",
            use_container_width=True
        ):

            if first_name == second_name:

                st.warning(
                    "Escolhe dois animais diferentes."
                )

            else:

                first = next(
                    x for x in animals
                    if animal_name(x) == first_name
                )

                second = next(
                    x for x in animals
                    if animal_name(x) == second_name
                )

                st.session_state.fusion_result = {
                    "first": first,
                    "second": second
                }

        if st.session_state.fusion_result:

            result = st.session_state.fusion_result

            st.markdown("---")

            st.markdown(
                "## 🧬 Resultado da fusão"
            )

            st.success(
                f"✨ {animal_name(result['first'])} + "
                f"{animal_name(result['second'])}"
            )

            st.markdown(
                """
                Esta é uma combinação fictícia criada
                apenas para fins de exploração e diversão.
                """
            )


# ============================================================
# QUIZ
# ============================================================

elif st.session_state.page == "🧠 Quiz":

    st.title(
        "🧠 Quiz"
    )

    quiz_animals = only_animals(
        st.session_state.last_animals
        + st.session_state.favorites
    )

    unique = {}

    for animal in quiz_animals:

        animal_id = animal.get("id")

        if animal_id:
            unique[animal_id] = animal

    quiz_animals = list(unique.values())

    if len(quiz_animals) < 3:

        st.info(
            "Pesquisa alguns animais primeiro para começar o quiz."
        )

    else:

        animal = random.choice(
            quiz_animals
        )

        correct = animal_name(animal)

        options = [
            correct
        ]

        others = [
            animal_name(x)
            for x in quiz_animals
            if animal_name(x) != correct
        ]

        random.shuffle(others)

        options.extend(
            others[:3]
        )

        random.shuffle(options)

        st.markdown(
            "### 🐾 Que animal é este?"
        )

        photo = safe_photo(animal)

        if photo:

            st.image(
                photo,
                width=300
            )

        answer = st.radio(
            "Escolhe a resposta:",
            options
        )

        if st.button(
            "✅ Responder",
            use_container_width=True
        ):

            st.session_state.quiz_total += 1

            if answer == correct:

                st.session_state.quiz_score += 1

                st.success(
                    "🎉 Resposta correta!"
                )

            else:

                st.error(
                    f"❌ A resposta correta era {correct}."
                )

        st.markdown("---")

        st.metric(
            "Pontuação",
            f"{st.session_state.quiz_score}/"
            f"{st.session_state.quiz_total}"
        )


# ============================================================
# CONQUISTAS
# ============================================================

elif st.session_state.page == "🏆 Conquistas":

    st.title(
        "🏆 Conquistas"
    )

    favorites_count = len(
        st.session_state.favorites
    )

    rescued_count = len(
        st.session_state.rescued
    )

    quiz_total = st.session_state.quiz_total

    achievements = []

    if favorites_count >= 1:
        achievements.append(
            "❤️ Primeiro favorito"
        )

    if favorites_count >= 5:
        achievements.append(
            "🌟 Colecionador"
        )

    if rescued_count >= 1:
        achievements.append(
            "🚑 Primeiro resgate"
        )

    if quiz_total >= 5:
        achievements.append(
            "🧠 Mestre do Quiz"
        )

    if not achievements:

        st.info(
            "Ainda não desbloqueaste nenhuma conquista."
        )

    else:

        for achievement in achievements:

            st.success(
                f"🏆 {achievement}"
            )


# ============================================================
# ESTATÍSTICAS
# ============================================================

elif st.session_state.page == "📊 Estatísticas":

    st.title(
        "📊 Estatísticas"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "❤️ Favoritos",
            len(st.session_state.favorites)
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🚑 Resgates",
            len(st.session_state.rescued)
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🩺 Veterinário",
            len(st.session_state.veterinary)
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            '<div class="stat-box">',
            unsafe_allow_html=True
        )

        st.metric(
            "🧠 Quiz",
            st.session_state.quiz_score
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# DEFINIÇÕES
# ============================================================

elif st.session_state.page == "⚙️ Definições":

    st.title(
        "⚙️ Definições"
    )

    st.markdown(
        "### 🌍 MundoVivo"
    )

    st.write(
        "Explora a biodiversidade do planeta."
    )

    st.markdown("---")

    st.markdown(
        "### 📊 Dados da sessão"
    )

    st.write(
        f"❤️ Favoritos: {len(st.session_state.favorites)}"
    )

    st.write(
        f"🚑 Resgates: {len(st.session_state.rescued)}"
    )

    st.write(
        f"🩺 Consultas: {len(st.session_state.veterinary)}"
    )

    st.markdown("---")

    if st.button(
        "🗑️ Limpar dados da sessão",
        use_container_width=True
    ):

        st.session_state.favorites = []
        st.session_state.rescued = []
        st.session_state.veterinary = []
        st.session_state.last_animals = []
        st.session_state.search_results = []
        st.session_state.fusion_result = None
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0

        st.success(
            "Dados da sessão limpos."
        )

        time.sleep(1)

        st.rerun()


# ============================================================
# RODAPÉ
# ============================================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <div class="small-text">
    🌍 MundoVivo<br>
    Explorar • Aprender • Proteger
    </div>
    """,
    unsafe_allow_html=True
)
