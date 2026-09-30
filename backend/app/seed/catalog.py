"""Copy taken from cherry-studios-site/ and docs/sdd/01-especificacion.md."""

SERVICES: tuple[dict[str, str], ...] = (
    {
        "slug": "composicion",
        "number_label": "01",
        "title": "Composición",
        "icon": "composicion",
        "short_description": (
            "Desarrollo de idea, letra, estructura y arreglos desde cero — "
            "solo o junto a Chemita y Ramzy."
        ),
    },
    {
        "slug": "grabacion",
        "number_label": "02",
        "title": "Grabación",
        "icon": "grabacion",
        "short_description": (
            "Tracking, comping y entrega de sesión, stems o multitrack, "
            "con acompañamiento en cabina."
        ),
    },
    {
        "slug": "mezcla",
        "number_label": "03",
        "title": "Mezcla",
        "icon": "mezcla",
        "short_description": (
            "Balance, espacio y textura en estéreo para que cada elemento "
            "de tu canción tenga su lugar."
        ),
    },
    {
        "slug": "master",
        "number_label": "04",
        "title": "Máster",
        "icon": "master",
        "short_description": (
            "El acabado final: loudness, translación entre bocinas y "
            "consistencia entre plataformas."
        ),
    },
    {
        "slug": "producciones",
        "number_label": "05",
        "title": "Producciones",
        "icon": "producciones",
        "short_description": (
            "Desde la composición hasta la entrega final de tu máster para EP o álbum."
        ),
    },
    {
        "slug": "beat-making",
        "number_label": "06",
        "title": "Beat Making",
        "icon": "beat-making",
        "short_description": (
            "Beats exclusivos o personalizados, construidos desde cero para tu proyecto."
        ),
    },
    {
        "slug": "podcast",
        "number_label": "07",
        "title": "Grabación de podcast",
        "icon": "podcast",
        "short_description": (
            "Grabación multipista para conversaciones y episodios, lista para editar y publicar."
        ),
    },
    {
        "slug": "post-audiovisual",
        "number_label": "08",
        "title": "Post audiovisual",
        "icon": "post-audiovisual",
        "short_description": "Edición y mezcla de audio para video, clips y contenido audiovisual.",
    },
)

TEAM: tuple[dict[str, str], ...] = (
    {
        "slug": "alejandro-vega",
        "full_name": "Alejandro Vega",
        "nickname": "Chemita",
        "role_label": "Producción vocal · Mezcla · Mastering",
        "bio_short": (
            "Se especializa en producción vocal, mezcla y mastering. Busca que cada canción "
            "transmita la emoción, intención y claridad que el artista se imaginó desde un inicio."
        ),
        "photo": "founder-1.jpg",
        "alt": "Retrato de Alejandro Vega, “Chemita”",
    },
    {
        "slug": "ramses-jimenez",
        "full_name": "Ramsés Jiménez",
        "nickname": "Ramzy",
        "role_label": "Ingeniería de audio · Producción",
        "bio_short": (
            "Se especializa en mezcla, composición y mastering, buscando que cada canción "
            "encuentre su propia identidad. Su enfoque combina creatividad y técnica para "
            "lograr un sonido sólido, cuidado y fiel a la visión del artista."
        ),
        "photo": "founder-2.jpg",
        "alt": "Retrato de Ramsés Jiménez Acosta, “Ramzy”",
    },
)

STUDIO_ALT = (
    "Chemita y Ramzy trabajando en la mesa de producción de Cherry Studios, "
    "monitores e interfaz encendidos."
)
PRIVACY_UPDATED_AT = "2026-08-04"
CONTACT_EMAIL = "contacto@cherrystudios.com.mx"
INSTAGRAM_URL = "https://www.instagram.com/_cherrystudios_/"
CONSENT_TEXT = (
    "Tus datos serán tratados por Cherry Studios para contactarte y dar seguimiento "
    "a tu solicitud. Consulta nuestro Aviso de Privacidad."
)
