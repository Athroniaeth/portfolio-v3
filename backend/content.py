"""Portfolio content: the single source of truth, in Python, in both languages.

The site is static, so nothing here is fetched at runtime by a visitor. `just content`
serialises these structs to `frontend/src/data/content.json`, the prerenderer bakes
that JSON into the HTML of every page — once per language — and the browser downloads
zero bytes of data on top of the markup. The same structs are still served on
/api/content, which is what keeps them honest: they appear in openapi.json, get typed
on the frontend, and stay available to a third party without a second definition.

Two conventions worth knowing before editing:

  - **Every visible string is a `Text`**, carrying its French and English versions
    side by side. Keeping the two in one place is what stops a translation from
    silently going missing: adding a field means filling both.
  - **Durations are never written down.** An entry carries a `Period` and the
    templates compute "1 an 8 mois" from it at build time. The previous site said
    "1 year, 2 month" about a job that had been running for twenty months, because
    the number had been typed by hand and then forgotten.

Editing the site means editing this file and running `just content`.
"""

from datetime import date
from typing import Literal

import msgspec


class Text(msgspec.Struct, frozen=True):
    """One string in both languages.

    `fr` first because French is the default locale: the site serves it at the root
    and English under /en/.
    """

    fr: str
    en: str


def both(value: str) -> Text:
    """A string that reads the same in both languages, such as a product name.

    Writing `both("Docker")` rather than `Text(fr="Docker", en="Docker")` keeps the
    skill lists legible, and keeps the intent visible: this is not a translation
    somebody forgot to write.
    """
    return Text(fr=value, en=value)


class Period(msgspec.Struct, frozen=True):
    """A span of time, open-ended when it is still running.

    Only the year and month matter — the day is always the 1st and is never rendered.
    `end=None` means "present", which the templates translate per locale.
    """

    start: date
    end: date | None = None


class SocialLink(msgspec.Struct, frozen=True):
    """A profile elsewhere. `icon` is a key into the frontend's icon set, not a URL:
    the SVGs are inlined in the bundle, so a social row costs no extra request."""

    platform: str
    href: str
    icon: str


class Project(msgspec.Struct, frozen=True):
    """`image` is a stem, not a path — "bresse", not "/images/bresse.png".

    The optimiser (`just images`) emits several widths in both AVIF and WebP for each
    source, and the frontend builds the <picture> srcset from the stem. Hardcoding one
    file name here would pin the page to a single format and a single width.

    `title` and `stack` stay untranslated on purpose: they are product and technology
    names, and translating "Game of life" or "Python" would be worse, not better.
    """

    title: str
    description: Text
    image: str
    link: str
    stack: list[str]
    repository: str | None = None
    # A write-up about the project. The URL itself is localised because the two
    # versions of the Medium article live at different addresses.
    article: Text | None = None


# What a timeline line actually is. Rendered as a distinct icon and a label, because
# a chess title and a master's degree drawn with the same tick in the same list read as
# the same kind of thing, which is how the previous version managed to make two
# runner-up finishes look like qualifications.
AchievementKind = Literal["experience", "education", "certification", "distinction"]


class Achievement(msgspec.Struct, frozen=True):
    """One line of the timeline, being a job, a diploma, a certification or a title.

    `period` is absent for anything instantaneous, such as a certification or a title
    won, and `url` carries the verification link when there is one to show.
    """

    title: Text
    description: Text
    kind: AchievementKind
    period: Period | None = None
    url: str | None = None


class TimelineEntry(msgspec.Struct, frozen=True):
    """A year of the timeline, and everything that started in it.

    The anchor is the **start** year, uniformly. The previous site mixed conventions —
    Fiducial filed under the year it began, the master's degree under the year it
    ended — which made the chronology impossible to read.
    """

    year: int
    achievements: list[Achievement]


class ContactMethod(msgspec.Struct, frozen=True):
    """`href` carries its own scheme (mailto:, tel:, https:) so the template stays
    dumb: it renders an anchor and never has to branch on the kind of contact."""

    label: Text
    value: str
    href: str


class LanguageSkill(msgspec.Struct, frozen=True):
    """`level` is optional because an unstated level is better than an invented one."""

    name: Text
    level: Text | None = None


class SkillGroup(msgspec.Struct, frozen=True):
    """A named cluster of skills, drawn as one card of the Compétences section.

    `items` are `Text` even where both sides read the same. A group holds "Docker",
    which must not be translated, next to "Méthodologie agile", which must be; one
    list of one type keeps that branch out of the template, and `both()` writes the
    untranslatable half without repeating it.
    """

    name: Text
    items: list[Text]


# A review is left at the end of a paid engagement and carries a rating; a
# recommendation is written by someone who worked alongside, outside any mission, and
# carries none. Labelling them differently is the honest thing to do, and it is also
# what lets the card know whether to draw stars.
TestimonialKind = Literal["review", "recommendation"]


class Testimonial(msgspec.Struct, frozen=True):
    """Something someone else said, quoted with its provenance.

    `source_url` is optional rather than required. Malt shows that a recommendation
    exists but hides its text behind a login, so linking there would send a reader to
    a page where they cannot find the quote. No link is better than a link that does
    not deliver what it promises.
    """

    quote: Text
    author: str
    kind: TestimonialKind
    published: date
    role: str | None = None
    company: str | None = None
    rating: int | None = None
    source: str = "Malt"
    source_url: str | None = None


class Profile(msgspec.Struct, frozen=True):
    name: str
    role: Text
    location: str
    headline: Text
    summary: Text
    about: Text


class SectionCopy(msgspec.Struct, frozen=True):
    """The three-line intro that opens a section."""

    heading: Text
    subheading: Text
    paragraph: Text


class Sections(msgspec.Struct, frozen=True):
    """Every section of the page, in the order it is rendered.

    The site used to be four documents, and this struct described only the blocks of
    the home page. It is now one document, so these field names double as the anchors
    the header links to, and `heading` doubles as the label of that link. A section
    with nothing to say would therefore be a nav entry pointing at nothing, which is
    why they are fields rather than a list.
    """

    about: SectionCopy
    projects: SectionCopy
    skills: SectionCopy
    timeline: SectionCopy
    testimonial: SectionCopy
    contact: SectionCopy


class Content(msgspec.Struct, frozen=True):
    """Everything the site renders. One struct, so one export and one import."""

    profile: Profile
    socials: list[SocialLink]
    projects: list[Project]
    timeline: list[TimelineEntry]
    contact: list[ContactMethod]
    skills: list[SkillGroup]
    languages: list[LanguageSkill]
    testimonials: list[Testimonial]
    sections: Sections


PROFILE = Profile(
    name="Pierre Chaumont",
    # "AI Engineer" in French too. The English title is what the French market uses
    # for this job, and "Ingénieur IA" would read as a translation of a job nobody
    # advertises under that name.
    role=Text(fr="AI Engineer", en="AI Engineer"),
    location="Bordeaux",
    headline=Text(
        fr="AI Engineer et Software Engineer, passionné de tech.",
        en="Software & AI Engineer, and tech enthusiast.",
    ),
    summary=Text(
        fr=(
            "Je m'appelle Pierre Chaumont, AI Engineer basé à Bordeaux. Je conçois et "
            "déploie des solutions locales, open source et auto-hébergées, qui allient "
            "robustesse technique et utilité métier. Je construis des API d'extraction "
            "documentaire, des chatbots connectés à la documentation interne (RAG), "
            "des agents outillés qui pilotent des services en langage naturel et des "
            "pipelines de traitement de données à grande échelle."
        ),
        en=(
            "My name is Pierre Chaumont, an AI Engineer based in Bordeaux. I design "
            "and ship local, open-source and self-hosted solutions that pair technical "
            "robustness with real business value. I build document extraction APIs, "
            "chatbots wired to internal documentation (RAG), tool-using agents that "
            "drive services in plain language, and large-scale data processing "
            "pipelines."
        ),
    ),
    about=Text(
        fr=(
            "AI Engineer spécialisé en software engineering, basé à Bordeaux, je "
            "conçois et déploie des solutions locales, via l'open source et l'auto- "
            "hébergé, alliant robustesse technique et utilité métier. Mon parcours m'a "
            "conduit à créer des API d'extraction documentaire, des chatbots connectés "
            "à la documentation interne (RAG), des agents outillés et des pipelines de "
            "traitement de données à grande échelle, tout en contribuant à la mise en "
            "production de systèmes IA utilisés quotidiennement. Diplômé d'un Master "
            "en IA & Big Data, j'accorde une importance particulière à la clarté, à la "
            "qualité du code et à la collaboration entre profils techniques et "
            "métiers. Curieux et rigoureux, j'aime transformer des idées complexes en "
            "produits simples, fiables et compréhensibles."
        ),
        en=(
            "An AI Engineer specialised in software engineering and based in Bordeaux, "
            "I design and ship local, open-source and self-hosted solutions that pair "
            "technical robustness with real business value. Along the way I have built "
            "document extraction APIs, chatbots wired to internal documentation (RAG), "
            "tool-using agents and large-scale data processing pipelines, and put AI "
            "systems into daily production use. I hold a master's degree in AI & Big "
            "Data, and I care about clarity, code quality and the collaboration "
            "between technical and business people. Curious and methodical, I like "
            "turning complex ideas into simple, reliable and understandable products."
        ),
    ),
)

SOCIALS = [
    SocialLink(
        platform="LinkedIn",
        href="https://www.linkedin.com/in/pierrechaumont69/",
        icon="linkedin",
    ),
    SocialLink(
        platform="GitHub",
        href="https://github.com/Athroniaeth",
        icon="github",
    ),
    SocialLink(
        platform="Malt",
        href="https://www.malt.fr/profile/pierrechaumont",
        icon="malt",
    ),
]

PROJECTS = [
    Project(
        title="PIIGhost",
        description=Text(
            fr=(
                "Bibliothèque Python qui empêche les données personnelles d'atteindre "
                "un modèle de langage, sans rien casser dans l'application. Les PII "
                "sont détectées (regex, NER ou un autre LLM) puis remplacées par des "
                "placeholders stables, si bien que john.doe@example.com devient "
                "<<EMAIL:1>>. Le modèle ne travaille que sur du texte dé-identifié, et "
                "les vraies valeurs sont réinjectées dans la réponse, sans que "
                "l'utilisateur voie jamais la dé-identification. Un outil appelé par "
                "l'agent reçoit la valeur réelle, quand le LLM qui décide de l'appeler "
                "ne voit que le placeholder. Autour de la bibliothèque gravitent une "
                "API d'inférence, un hub, une application de démonstration et un "
                "design system."
            ),
            en=(
                "A Python library that keeps personal data out of a language model "
                "without breaking the application around it. PII is detected (regex, "
                "NER or another LLM) and replaced with stable placeholders, so that "
                "john.doe@example.com becomes <<EMAIL:1>>. The model only ever works "
                "on de-identified text, and the real values are restored in the "
                "response, so the end user never sees the de-identification. A tool "
                "called by the agent receives the real value, while the LLM deciding "
                "to call it still sees only the placeholder. Around the library sit an "
                "inference API, a hub, a demo application and a design system."
            ),
        ),
        image="piighost",
        # The product site, not the repository. `repository` below is rendered as a
        # separate "Code" link, so the card's headline destination can be the page that
        # explains what the thing does rather than a README.
        link="https://piighost.dev/",
        repository="https://github.com/Athroniaeth/piighost",
        stack=["Python", "NLP", "Privacy", "LLM"],
    ),
    Project(
        title="Keyshield",
        description=Text(
            fr=(
                "Système de clés d'API sécurisé et prêt pour la production, agnostique "
                "du framework. Stratégies de hachage interchangeables (Argon2, bcrypt "
                "ou la vôtre), persistance au choix (SQLAlchemy, en mémoire, dépôt sur "
                "mesure) et couche de cache optionnelle (aiocache, Redis). "
                "Intégrations fournies pour FastAPI, Litestar, Django et Quart, plus "
                "une CLI Typer pour la gestion des clés. Anciennement fastapi-api-key."
            ),
            en=(
                "A secure, production-ready API key system, agnostic of the framework "
                "around it. Pluggable hashing strategies (Argon2, bcrypt or your "
                "own), backend-agnostic persistence (SQLAlchemy, in-memory, or your "
                "own repository) and an optional cache layer (aiocache, Redis). Ships "
                "integrations for FastAPI, Litestar, Django and Quart, plus a Typer "
                "CLI to manage keys. Formerly fastapi-api-key."
            ),
        ),
        image="keyshield-schema",
        link="https://github.com/Athroniaeth/keyshield",
        repository="https://github.com/Athroniaeth/keyshield",
        stack=["Python", "FastAPI", "Litestar", "Software Engineering"],
    ),
    Project(
        title="Bresse",
        description=Text(
            fr=(
                "Bibliothèque qui fait jouer un LLM aux échecs, en exploitant le fait "
                "qu'un modèle sait reproduire le format PGN d'une partie. Elle fournit "
                "de quoi mener des expériences, modifier le PGN en cours d'inférence "
                "et instrumenter les parties. Le point de départ était de vérifier si "
                "ChatGPT tient réellement une partie de 80 coups sans coup illégal."
            ),
            en=(
                "A library that makes an LLM play chess, taking advantage of the fact "
                "that a model can reproduce the PGN format of a game. It provides the "
                "tooling to run experiments, edit the PGN during inference and "
                "instrument games. It started as a way to check whether ChatGPT really "
                "holds an 80-move game together without an illegal move."
            ),
        ),
        image="bresse",
        link="https://github.com/Athroniaeth/bresse",
        repository="https://github.com/Athroniaeth/bresse",
        stack=["Python", "Langchain", "LLM"],
        article=Text(
            fr="https://medium.com/@Athroniaeth/chatgpt-peut-jouer-une-partie-d%C3%A9checs-de-80-coups-sans-coups-ill%C3%A9gaux-a9052ff3b603",
            en="https://medium.com/@Athroniaeth/chatgpt-can-play-a-chess-game-of-80-moves-without-illegal-moves-74b5a30bd13a",
        ),
    ),
    Project(
        title="Chat PDF",
        description=Text(
            fr=(
                "Chatbot pour dialoguer avec des PDF via un système RAG qui ne fournit "
                "au modèle que les extraits pertinents du document. Une mémoire de "
                "conversation est intégrée, ce qui permet de longues discussions avec "
                "un même document."
            ),
            en=(
                "A chatbot for talking to PDFs through a RAG system that hands the "
                "model only the relevant chunks of the document. A chat memory is "
                "built in, which allows long discussions with a single document."
            ),
        ),
        image="chat-pdf",
        link="https://github.com/Athroniaeth/chat-pdf",
        repository="https://github.com/Athroniaeth/chat-pdf",
        stack=["Python", "Langchain", "RAG"],
    ),
    Project(
        title="Master fisher",
        description=Text(
            fr=(
                "Bot de pêche pour World of Warcraft, entièrement automatique. Les "
                "clics et mouvements de souris se font dans le jeu, sans aucune "
                "intervention humaine. Une page web permet de suivre en direct ce que "
                "le bot est en train de faire."
            ),
            en=(
                "A fishing bot for World of Warcraft, fully automatic. Mouse clicks "
                "and movements happen inside the game with no human intervention, and "
                "a web page lets you watch live what the bot is doing."
            ),
        ),
        image="masterfisher",
        link="https://github.com/Athroniaeth/masterfisher",
        repository="https://github.com/Athroniaeth/masterfisher",
        stack=["Python", "PyTorch", "OpenCV"],
    ),
    Project(
        title="Game of life",
        description=Text(
            fr=(
                "Le jeu de la vie de Conway, rendu en temps réel avec Pygame. Une "
                "grille de cellules dont les règles de naissance et de mort font "
                "émerger planeurs, oscillateurs et structures stables en quelques "
                "lignes de code."
            ),
            en=(
                "Conway's Game of Life, rendered in real time with Pygame. A grid of "
                "cells whose birth and death rules produce gliders, oscillators and "
                "still lifes out of a handful of lines of code."
            ),
        ),
        image="game-of-life",
        link="https://github.com/Athroniaeth/game-of-life",
        repository="https://github.com/Athroniaeth/game-of-life",
        stack=["Python", "Pygame"],
    ),
]

TIMELINE = [
    TimelineEntry(
        year=2025,
        achievements=[
            Achievement(
                title=Text(
                    fr="AI Engineer chez FIDUCIAL",
                    en="AI Engineer at FIDUCIAL",
                ),
                description=Text(
                    fr=(
                        "Conception d'une API de traitement de documents non "
                        "structurés, avec parsing, classification et extraction. Elle "
                        "tourne en production autour de 20 000 requêtes par mois sur "
                        "des documents notariaux. Industrialisation d'un socle RAG "
                        "commun, décliné en chatbots métier pour les notaires, "
                        "garagistes, pharmaciens et les autres activités du groupe. "
                        "Conception d'une API d'orchestration de LLM sur modèles "
                        "locaux, avec gestion du contexte et mémoire persistante, et "
                        "développement d'agents outillés qui pilotent des services et "
                        "des briques data en langage naturel, comme Matomo ou "
                        "Supabase. Mise en place de la plateforme d'observabilité qui "
                        "va avec."
                    ),
                    en=(
                        "Design of an API for processing unstructured documents, with "
                        "parsing, classification and extraction. It runs in production "
                        "at around 20,000 requests a month on notarial documents. "
                        "Industrialisation of a shared RAG foundation, turned into "
                        "business chatbots for the group's notaries, garages, "
                        "pharmacies and its other lines of work. Design of an LLM "
                        "orchestration API running on local models, with context "
                        "handling and persistent memory, and of tool-using agents that "
                        "drive services and data components in plain language, such as "
                        "Matomo or Supabase. Plus the observability platform that goes "
                        "with all of it."
                    ),
                ),
                period=Period(start=date(2025, 1, 1)),
                kind="experience",
            ),
        ],
    ),
    TimelineEntry(
        year=2024,
        achievements=[
            Achievement(
                title=Text(
                    fr="Certification « AI-Powered Software and System Design »",
                    en='"AI-Powered Software and System Design" certification',
                ),
                description=Text(
                    fr=(
                        "Certification DeepLearning.AI validant la conception "
                        "d'architectures logicielles assistée par l'IA, la création et "
                        "l'optimisation de bases de données avec l'aide de LLM, et "
                        "l'application de patrons de conception avancés."
                    ),
                    en=(
                        "A DeepLearning.AI certification covering AI-assisted software "
                        "architecture design, building and optimising databases with "
                        "the help of LLMs, and applying advanced design patterns."
                    ),
                ),
                url="https://www.coursera.org/account/accomplishments/verify/8FU5N657OBT4",
                kind="certification",
            ),
            Achievement(
                title=Text(
                    fr="Certification « Introduction to Data and Data Science »",
                    en='"Introduction to Data and Data Science" certification',
                ),
                description=Text(
                    fr="Certification 365 Data Science.",
                    en="A 365 Data Science certification.",
                ),
                url="https://learn.365datascience.com/certificates/CC-251B5E9E94/",
                kind="certification",
            ),
            Achievement(
                title=Text(
                    fr="Certification « Introduction to Python »",
                    en='"Introduction to Python" certification',
                ),
                description=Text(
                    fr="Certification 365 Data Science.",
                    en="A 365 Data Science certification.",
                ),
                url="https://learn.365datascience.com/certificates/CC-BE67D8BFDB/",
                kind="certification",
            ),
        ],
    ),
    TimelineEntry(
        year=2023,
        achievements=[
            Achievement(
                title=Text(
                    fr="Data Scientist chez Arkema, en freelance",
                    en="Data Scientist at Arkema, freelance",
                ),
                description=Text(
                    fr=(
                        "Mission menée en parallèle des postes chez Scalian puis "
                        "FIDUCIAL, avec l'accord de l'employeur et hors temps de "
                        "travail. Développement de pipelines de données et d'outils "
                        "d'IA, avec suivi de la qualité et livraison dans des délais "
                        "courts."
                    ),
                    en=(
                        "Run alongside the Scalian and then FIDUCIAL positions, with "
                        "the employer's agreement and outside working hours. Building "
                        "data pipelines and AI tooling, with quality follow-up and "
                        "delivery on short timelines."
                    ),
                ),
                period=Period(start=date(2023, 10, 1), end=date(2025, 5, 1)),
                kind="experience",
            ),
            Achievement(
                title=Text(
                    fr="Data Scientist chez Scalian",
                    en="Data Scientist at Scalian",
                ),
                description=Text(
                    fr=(
                        "Au sein d'une équipe data de cinq personnes, conception et "
                        "industrialisation d'un pipeline d'OCR pour extraire de "
                        "manière structurée les données de millions de plans "
                        "cadastraux manuscrits, avec la responsabilité de la mise en "
                        "production. Développement de plusieurs systèmes à base d'IA "
                        "déployés sur une infrastructure cloud, dont un chatbot "
                        "d'analyse de projets GitLab, la génération automatique de "
                        "tests unitaires et la simulation de pollution urbaine."
                    ),
                    en=(
                        "Within a five-person data team, design and industrialisation "
                        "of an OCR pipeline extracting structured data from millions "
                        "of handwritten cadastral plans, owning the move to "
                        "production. Development of several AI-driven systems deployed "
                        "on cloud infrastructure, among them a GitLab project analysis "
                        "chatbot, automated unit test generation and urban pollution "
                        "simulation."
                    ),
                ),
                period=Period(start=date(2023, 11, 1), end=date(2024, 5, 1)),
                kind="experience",
            ),
        ],
    ),
    TimelineEntry(
        year=2021,
        achievements=[
            Achievement(
                title=Text(
                    fr="Data Scientist chez Arkema, en alternance",
                    en="Data Scientist at Arkema, apprenticeship",
                ),
                description=Text(
                    fr=(
                        "Au service achat, développement de modèles prédictifs "
                        "d'évolution des prix fournisseurs, connectés à des tableaux "
                        "de bord Power BI. Création d'une bibliothèque Python "
                        "automatisant les workflows ETL SAP derrière une interface "
                        "graphique. Développement d'une application web de "
                        "questionnaires intégrée à Microsoft Teams et pilotée par les "
                        "données d'interaction."
                    ),
                    en=(
                        "In the purchasing department, predictive machine learning "
                        "models for supplier price evolution, wired to Power BI "
                        "dashboards. A Python library automating SAP ETL workflows "
                        "behind a graphical interface. And a dynamic web questionnaire "
                        "application integrated with Microsoft Teams and driven by "
                        "interaction data."
                    ),
                ),
                period=Period(start=date(2021, 9, 1), end=date(2023, 9, 1)),
                kind="experience",
            ),
            Achievement(
                title=Text(
                    fr="Master IA & Big Data, ESGI",
                    en="Master's degree in AI & Big Data, ESGI",
                ),
                description=Text(
                    fr=(
                        "Deep learning, traitement automatique de la langue, "
                        "apprentissage par renforcement, BI et Big Data, Spark et "
                        "programmation fonctionnelle, cloud et automatisation pour le "
                        "machine learning, gestion de projet SI et méthodologie agile."
                    ),
                    en=(
                        "Deep learning, natural language processing, deep "
                        "reinforcement learning, BI and Big Data, Spark and functional "
                        "programming, cloud and automation for machine learning, IT "
                        "project management and agile methodology."
                    ),
                ),
                period=Period(start=date(2021, 9, 1), end=date(2023, 6, 1)),
                kind="education",
            ),
            Achievement(
                title=Text(
                    fr="Développeur web à l'Université Claude Bernard Lyon 1",
                    en="Web developer at Université Claude Bernard Lyon 1",
                ),
                description=Text(
                    fr=(
                        "Développement d'une application web de gestion de tickets et "
                        "de réservation de créneaux sur un spectromètre."
                    ),
                    en=(
                        "Development of a web application for ticket management and "
                        "for booking time slots on a spectrometer."
                    ),
                ),
                period=Period(start=date(2021, 2, 1), end=date(2021, 4, 1)),
                kind="experience",
            ),
        ],
    ),
    TimelineEntry(
        year=2020,
        achievements=[
            Achievement(
                title=Text(
                    fr="Bachelor Chef de projet architecture des logiciels, ESGI",
                    en="Bachelor's degree in software architecture & project "
                    "management, ESGI",
                ),
                description=Text(
                    fr=(
                        "Scripting Python, C et Java avancés, API Node.js, frontend "
                        "Angular, tests unitaires, algorithmique avancée, conception "
                        "de bases de données relationnelles, intelligence "
                        "artificielle, Linux et gestion de projet agile."
                    ),
                    en=(
                        "Python scripting, advanced C and Java, Node.js APIs, Angular "
                        "front ends, unit testing, advanced algorithms, relational "
                        "database design, artificial intelligence, Linux and agile "
                        "project management."
                    ),
                ),
                period=Period(start=date(2020, 9, 1), end=date(2021, 6, 1)),
                kind="education",
            ),
        ],
    ),
    TimelineEntry(
        year=2019,
        achievements=[
            Achievement(
                title=Text(
                    fr="Vice-champion junior du Championnat Régional Jeune",
                    en="Junior runner-up, Regional Youth Championship",
                ),
                description=Text(
                    fr=(
                        "Échecs, C.R.M.L.E. Le jeu est resté, puisque le projet "
                        "Bresse fait jouer un LLM aux échecs et que chess_pytorch_ai "
                        "cherche à en faire jouer un réseau de neurones."
                    ),
                    en=(
                        "Échecs, C.R.M.L.E. The game stuck around, since the Bresse "
                        "project makes an LLM play chess and chess_pytorch_ai tries to "
                        "get a neural network to do the same."
                    ),
                ),
                kind="distinction",
            ),
            Achievement(
                title=Text(
                    fr="Vice-champion junior du Championnat de Ligue ARA",
                    en="Junior runner-up, ARA League Championship",
                ),
                description=Text(fr="Échecs, Ligue ARA.", en="Chess, ARA League."),
                kind="distinction",
            ),
        ],
    ),
    TimelineEntry(
        year=2018,
        achievements=[
            Achievement(
                title=Text(
                    fr="BTS Services informatiques aux organisations",
                    en="Associate's degree in IT services for organisations",
                ),
                description=Text(
                    fr=(
                        "Bases du développement logiciel, des réseaux et de la gestion "
                        "des systèmes d'information."
                    ),
                    en=(
                        "Foundations in software development, networking and "
                        "information systems management."
                    ),
                ),
                kind="education",
                # Dated from the CV of 16/08/2026, which lists "2018 - 2020 : BTS SIO
                # à l'ESGI Lyon". It had no period at all before, because LinkedIn
                # gives none and 2018 was a deduction from the Bachelor starting in
                # September 2020.
                period=Period(date(2018, 9, 1), date(2020, 6, 1)),
            ),
        ],
    ),
]

# No phone number. It was on the previous site, and a personal mobile published on a
# public page is scraped within days; e-mail, LinkedIn and Malt cover the same need
# without leaving a number in every crawler's index. Add one back here if a client
# channel is genuinely missing.
CONTACT = [
    ContactMethod(
        label=Text(fr="LinkedIn", en="LinkedIn"),
        value="/in/pierrechaumont69",
        href="https://www.linkedin.com/in/pierrechaumont69/",
    ),
    ContactMethod(
        label=Text(fr="Malt", en="Malt"),
        value="/profile/pierrechaumont",
        href="https://www.malt.fr/profile/pierrechaumont",
    ),
    ContactMethod(
        label=Text(fr="E-mail", en="Email"),
        value="pierre.chaumont@hotmail.fr",
        href="mailto:pierre.chaumont@hotmail.fr",
    ),
]

LANGUAGES = [
    LanguageSkill(
        name=Text(fr="Français", en="French"),
        level=Text(fr="Langue maternelle", en="Native"),
    ),
    LanguageSkill(
        name=Text(fr="Anglais", en="English"),
        # LinkedIn and Malt both list English with no level, so the site carried none
        # either rather than invent one. The CV says "anglais professionnel TOEIC",
        # which is a stated level and settles it.
        level=Text(fr="Professionnel (TOEIC)", en="Professional (TOEIC)"),
    ),
]

# Straight from the CV, grouped so the section reads as four short lists instead of one
# wall of logos. Nothing here is aspirational: a tool is listed because it has been used
# in production or in one of the projects above.
SKILLS = [
    SkillGroup(
        name=Text(fr="Langages et frameworks", en="Languages and frameworks"),
        items=[both("Python"), both("FastAPI"), both("Litestar"), both("PyTorch")],
    ),
    SkillGroup(
        name=Text(fr="IA et LLM", en="AI and LLMs"),
        items=[both("LangChain"), both("LangGraph"), both("Qdrant"), both("Langfuse")],
    ),
    SkillGroup(
        name=Text(fr="Infrastructure", en="Infrastructure"),
        items=[
            both("Docker"),
            both("Docker Swarm"),
            both("Kubernetes"),
            both("MLflow"),
            both("Git"),
            both("OVH Cloud"),
        ],
    ),
    SkillGroup(
        name=Text(fr="Méthodes", en="Ways of working"),
        items=[
            Text(fr="Méthodologie agile", en="Agile methodology"),
            Text(fr="Management de projet SI", en="IT project management"),
            Text(fr="Gamification", en="Gamification"),
        ],
    ),
    SkillGroup(
        name=Text(fr="À côté", en="Outside work"),
        items=[
            Text(fr="Échecs en club", en="Club chess"),
            Text(fr="Guitare", en="Guitar"),
            Text(fr="Voyages", en="Travel"),
        ],
    ),
]

TESTIMONIALS = [
    Testimonial(
        quote=Text(
            fr=(
                "Je recommande vivement Pierre pour toute opportunité dans le domaine "
                "de la Data et de l'Intelligence Artificielle. Pierre a démontré des "
                "compétences exceptionnelles dans ces domaines, alliant une solide "
                "compréhension théorique à une application pratique remarquable. De "
                "plus, Pierre a toujours fait preuve d'un grand professionnalisme, "
                "d'une excellente éthique de travail et d'une volonté constante "
                "d'apprendre et de s'améliorer."
            ),
            en=(
                "I highly recommend Pierre for any opportunity in Data and Artificial "
                "Intelligence. Pierre has shown exceptional skill in these areas, "
                "pairing a solid theoretical grasp with remarkable practical "
                "application. He has also consistently shown great professionalism, "
                "an excellent work ethic and a constant willingness to learn and "
                "improve."
            ),
        ),
        author="Cedric",
        kind="review",
        published=date(2024, 11, 21),
        company="Arkema",
        rating=5,
        source_url="https://www.malt.fr/profile/pierrechaumont",
    ),
    Testimonial(
        quote=Text(
            fr=(
                "J'ai pu travailler aux côtés de mon collègue sur divers projets open "
                "source, cela a été une super expérience. Pierre a un profil Data "
                "Scientist avec une bonne appétence en ingénierie logicielle, maniant "
                "Git, CI/CD, Docker, et le cloud. Sa rigueur dans l'application de "
                "pratiques de développement garantit une bonne pérennité de travail. "
                "Avec un bon esprit de collaboration et un bon dévouement pour l'open "
                "source."
            ),
            en=(
                "I got to work alongside my colleague on various open source "
                "projects, and it was a great experience. Pierre has a Data Scientist "
                "profile with a real appetite for software engineering, handling Git, "
                "CI/CD, Docker and the cloud. His rigour in applying development "
                "practices is what makes the work last. Add a good collaborative "
                "spirit and a real dedication to open source."
            ),
        ),
        author="Gabriel P.",
        kind="recommendation",
        published=date(2024, 11, 21),
        role="Data Scientist",
        # No source_url on purpose. The recommendation is listed on the Malt profile,
        # but its text is only readable once signed in, so a link would promise a quote
        # the reader cannot reach.
    ),
]


SECTIONS = Sections(
    about=SectionCopy(
        heading=Text(fr="À propos", en="About"),
        subheading=Text(fr="Qui je suis.", en="Who I am."),
        paragraph=Text(
            fr="Quelques lignes sur mon parcours et ma façon de travailler.",
            en="A few lines on my background and how I work.",
        ),
    ),
    projects=SectionCopy(
        heading=Text(fr="Projets", en="Projects"),
        subheading=Text(
            fr="J'aime construire des choses.", en="I love building things."
        ),
        paragraph=Text(
            fr="Voici quelques-uns des projets sur lesquels j'ai travaillé.",
            en="Here are some of the projects I've worked on.",
        ),
    ),
    skills=SectionCopy(
        heading=Text(fr="Compétences", en="Skills"),
        subheading=Text(fr="Ce que j'utilise.", en="What I work with."),
        paragraph=Text(
            fr="Les outils que je pratique au quotidien, et ce qu'il y a autour.",
            en="The tools I work with day to day, and what sits around them.",
        ),
    ),
    timeline=SectionCopy(
        heading=Text(fr="Parcours", en="Timeline"),
        subheading=Text(fr="Mon changelog.", en="My life changelog."),
        paragraph=Text(
            fr="Le parcours, les diplômes et quelques titres au passage.",
            en="The path, the diplomas, and a few titles along the way.",
        ),
    ),
    testimonial=SectionCopy(
        heading=Text(fr="Retours", en="Testimonials"),
        subheading=Text(fr="Ce qu'on en dit.", en="What it is like to work with me."),
        paragraph=Text(
            fr="Avis de fin de mission et recommandations de personnes avec qui j'ai travaillé.",
            en="End-of-engagement reviews and recommendations from people I have worked with.",
        ),
    ),
    contact=SectionCopy(
        heading=Text(fr="Contact", en="Contact"),
        subheading=Text(fr="Parlons-en.", en="Let's talk."),
        paragraph=Text(
            fr="Une question, ou une envie de travailler ensemble ? Écrivez-moi, je réponds.",
            en="A question, or an idea to work on together? Write to me, I answer.",
        ),
    ),
)

CONTENT = Content(
    profile=PROFILE,
    socials=SOCIALS,
    projects=PROJECTS,
    timeline=TIMELINE,
    contact=CONTACT,
    skills=SKILLS,
    languages=LANGUAGES,
    testimonials=TESTIMONIALS,
    sections=SECTIONS,
)
