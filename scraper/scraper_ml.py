import requests
from bs4 import BeautifulSoup
from config import CIUDADES_POR_ZONA, generar_url
from processing import procesar_caracteristicas
import time
import pandas as pd
from datetime import datetime
import random

headers = {
    "User-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
}


def conectar_a_web(url, max_reintentos=3):
    """
    Se conecta a una URL con reintentos automáticos

    Args:
        url: URL a scrapear
        max_reintentos: Número de intentos antes de rendirse

    Returns:
        HTML de la página o None si falla
    """
    for intento in range(1, max_reintentos + 1):
        try:
            time.sleep(random.randint(7, 10))
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                if intento > 1:
                    print(f"✓ Conectado (intento {intento})")
                return response.text
            else:
                print(
                    f"✗ Status {response.status_code} (intento {intento}/{max_reintentos})"
                )
                if intento < max_reintentos:
                    time.sleep(10)  # Esperar más antes de reintentar

        except requests.exceptions.RequestException as e:
            print(f"✗ Error de red (intento {intento}/{max_reintentos}): {e}")
            if intento < max_reintentos:
                print(" Reintentando en 10 segundos...")
                time.sleep(10)

    # Si llegamos acá, fallaron todos los intentos
    print(f"✗ FALLÓ después de {max_reintentos} intentos. Continuando con siguiente...")
    return None


def extraer_precio(element):
    # Obteniendo precio
    try:
        contenedor_precio = element.find("div", class_="poly-price__current")
        if contenedor_precio:
            link = contenedor_precio.find("span", class_="andes-money-amount__fraction")
            if link:
                return link.get_text()
        return None
    except Exception as e:
        print(f"Error extrayendo precio: {e}")
        return None


def extraer_caracteristicas(element):
    # Obteniendo ambientes, baños y area
    try:
        contenedor_caracteristicas = element.find("ul", class_="poly-attributes_list")
        caracteristicas = contenedor_caracteristicas.find_all("li")
        array_caracteristicas = []
        for item in caracteristicas:
            array_caracteristicas.append(item.get_text())
        return array_caracteristicas

    except Exception as e:
        print(f"Error extrayendo caracteristicas: {e}")
        return None


def extraer_url(element):
    """Extrae la URL de la publicación"""
    try:
        link = element.find("a", href=True)
        if link:
            return link["href"]
        return None
    except Exception as e:
        print(f"Error extrayendo URL: {e}")
        return None


def extraer_data(html, zona, ciudad):
    soup = BeautifulSoup(html, "html.parser")
    df_data = []
    try:
        # Bloque de casas
        casas_individuales = soup.find_all("div", class_="poly-card__content")

    except Exception as e:
        print(f"Error al procesar el bloque de casas: {e}")
        exit()

    for element in casas_individuales:
        precio = extraer_precio(element)
        caracteristicas_raw = extraer_caracteristicas(element)
        caracteristicas = procesar_caracteristicas(caracteristicas_raw)
        # Verificar que hay al menos 3 características
        if caracteristicas and len(caracteristicas) >= 3:
            url_publicacion = extraer_url(element)
            fecha_scraping = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df_data.append(
                {
                    "fecha_scraping": fecha_scraping,
                    "zona": zona,
                    "ciudad": ciudad,
                    "precio": precio,
                    "ambientes": caracteristicas["amb"],
                    "bathrooms": caracteristicas["banos"],
                    "area": caracteristicas["m2"],
                    "url": url_publicacion,
                }
            )
        else:
            # Manejar caso donde faltan datos
            df_data.append(
                {
                    "precio": precio,
                    "ambientes": None,
                    "bathrooms": None,
                    "area": None,
                }
            )
    return df_data


def guardar_en_csv(df, mostrar_mensaje=True):
    df_raw = pd.DataFrame(df)
    df_raw.to_csv("./data/data.csv", index=False)
    if mostrar_mensaje:
        print("DataFrame guardado correctamente en: data.csv")


def main():
    todas_las_propiedades = []  # Acumular TODAS las propiedades

    # Importar MAX_PAGINAS desde config
    from config import MAX_PAGINAS

    print(f"\n{'=' * 60}")
    print(f"INICIANDO SCRAPING - Máximo {MAX_PAGINAS} páginas por ciudad")
    print(f"{'=' * 60}\n")

    # Loop por cada zona
    for zona, ciudades in CIUDADES_POR_ZONA.items():
        print(f"\n=== ZONA: {zona} ===")

        # Loop por cada ciudad de la zona
        for ciudad in ciudades:
            print(f"\n  → Ciudad: {ciudad}")
            propiedades_ciudad = 0  # Contador para esta ciudad

            # Loop por cada página
            for pagina in range(1, MAX_PAGINAS + 1):
                print(f"    Página {pagina}/{MAX_PAGINAS}...", end=" ")

                # Generar URL con paginación
                url = generar_url(zona, ciudad, pagina)

                # Scrapear
                try:
                    html = conectar_a_web(url)

                    # Si falló la conexión, saltar esta página
                    if html is None:
                        print("✗ Saltando esta página")
                        continue

                    propiedades = extraer_data(html, zona, ciudad)

                    # Si no hay propiedades, probablemente llegamos al final
                    if len(propiedades) == 0:
                        print("Sin resultados (fin de páginas)")
                        break

                    # Acumular
                    todas_las_propiedades.extend(propiedades)
                    propiedades_ciudad += len(propiedades)

                    print(f"✓ {len(propiedades)} propiedades")

                except Exception as e:
                    print(f"✗ Error: {e}")
                    # Continuar con la siguiente página
                    continue

            print(f"    TOTAL {ciudad}: {propiedades_ciudad} propiedades")

            # Guardar progreso después de cada ciudad
            if len(todas_las_propiedades) > 0:
                guardar_en_csv(todas_las_propiedades)
                print(
                    f"Progreso guardado ({len(todas_las_propiedades)} propiedades totales)"
                )

    print(f"\n{'=' * 60}")
    print("SCRAPING COMPLETADO")
    print(f"TOTAL GENERAL: {len(todas_las_propiedades)} propiedades")
    print(f"{'=' * 60}\n")

    # Guardar versión final
    if len(todas_las_propiedades) > 0:
        guardar_en_csv(todas_las_propiedades, mostrar_mensaje=True)
    else:
        print("No se obtuvieron propiedades")

    # Guardar todo en CSV
    guardar_en_csv(todas_las_propiedades, mostrar_mensaje=False)


if __name__ == "__main__":
    main()
