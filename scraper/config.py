# config.py

BASE_URL = "https://inmuebles.mercadolibre.com.ar/casas/venta"

MAX_PAGINAS = 42

# Mapeo de zonas a sus slugs en la URL
ZONAS_SLUGS = {
    "GBA Norte": "bsas-gba-norte",
    "GBA Oeste": "bsas-gba-oeste",
    "GBA Sur": "bsas-gba-sur",
    "Córdoba": "cordoba",
    "Costa Atlántica": "bsas-costa-atlantica",
    "Buenos Aires Interior": "buenos-aires-interior",
}

# Ciudades por zona (solo los slugs)
CIUDADES_POR_ZONA = {
    "GBA Norte": [
        "pilar",
        "escobar",
        "tigre",
        "san-isidro",
        "san-miguel",
        "general-san-martin",
        "vicente-lopez",
        "malvinas-argentina",
        "san-fernando",
    ],
    "GBA Oeste": [
        "la-matanza",
        "moron",
        "ituzaingo",
        "moreno",
        "merlo",
        "castelar",
        "tres-de-febrero",
        "hurlingham",
    ],
    "GBA Sur": [
        "la-plata",
        "esteban-echeverria",
        "quilmes",
        "lomas-de-zamora",
        "ezeiza",
        "berazategui",
        "lanus",
        "almirante-brown",
        "avellaneda",
    ],
    "Córdoba": ["cordoba", "punilla", "colon", "villa-carlos-paz", "santa-maria"],
    "Costa Atlántica": [
        "mar-del-plata",
        "costa-esmeralda",
        "pinamar",
        "mar-del-tuyu",
        "villa-gesell",
        "mar-de-ajo",
    ],
    "Buenos Aires Interior": ["lujan", "san-vicente"],
}


def generar_url(zona, ciudad, pagina=1):
    """
    Genera la URL de MercadoLibre para una zona, ciudad y página específica

    Args:
        zona: Nombre de la zona (ej: "GBA Norte")
        ciudad: Slug de la ciudad (ej: "pilar")
        pagina: Número de página (default 1)

    Returns:
        URL completa para scrapear
    """
    zona_slug = ZONAS_SLUGS[zona]

    # Calcular el offset para la paginación
    if pagina == 1:
        sufijo_paginacion = ""
    else:
        offset = (pagina - 1) * 48 + 1
        sufijo_paginacion = f"_Desde_{offset}"

    # Buenos Aires Interior tiene una estructura diferente
    if zona == "Buenos Aires Interior":
        return f"{BASE_URL}/venta/{zona_slug}/{ciudad}/{sufijo_paginacion}"

    return f"{BASE_URL}/{zona_slug}/{ciudad}/{sufijo_paginacion}"


def obtener_todas_las_urls():
    """Devuelve un diccionario con todas las URLs organizadas por zona"""
    urls = {}

    for zona, ciudades in CIUDADES_POR_ZONA.items():
        urls[zona] = {}
        for ciudad in ciudades:
            urls[zona][ciudad] = generar_url(zona, ciudad)

    return urls


UBICACIONES = obtener_todas_las_urls()

if __name__ == "__main__":
    print(obtener_todas_las_urls())
