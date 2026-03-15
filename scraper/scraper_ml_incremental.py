import requests
from bs4 import BeautifulSoup
from config import CIUDADES_POR_ZONA, generar_url
from processing import procesar_caracteristicas
import time
import pandas as pd
from datetime import datetime
import random
import json
import os
import sys

import sqlite3

headers = {
    "User-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
}


def crear_tabla_si_no_existe(db_path="../propiedades.db"):
    """
    Crea la tabla propiedades si no existe
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS propiedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_scraping TEXT NOT NULL,
            zona TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            precio INTEGER NOT NULL,
            ambientes INTEGER,
            bathrooms INTEGER,
            area INTEGER,
            url TEXT UNIQUE NOT NULL,
            precio_por_m2 REAL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Crear índice en URL para búsquedas rápidas (evitar duplicados)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_url ON propiedades(url)
    """)

    conn.commit()
    conn.close()
    print("Tabla 'propiedades' verificada/creada")


def guardar_en_db(propiedades, db_path="../propiedades.db"):
    """
    Inserta propiedades en la base de datos de forma incremental
    Evita duplicados basándose en la URL
    Guarda propiedades incluso con datos parciales (como el scraper original)
    """
    if not propiedades:
        return 0, 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    insertados = 0
    omitidos = 0

    for prop in propiedades:
        # Verificar que tenga al menos precio y url (mínimo indispensable)
        if not prop.get("precio") or not prop.get("url"):
            omitidos += 1
            continue

        # Verificar que el precio sea un número válido
        try:
            # Limpiar precio (quitar puntos de separador de miles argentinos)
            precio_limpio = (
                str(prop["precio"]).replace(".", "").replace(",", "").strip()
            )
            precio_val = int(precio_limpio)
            if precio_val <= 0:
                omitidos += 1
                continue
        except (ValueError, TypeError):
            omitidos += 1
            continue

        # Convertir valores opcionales (pueden ser None)
        try:
            amb_val = int(prop["ambientes"]) if prop.get("ambientes") else None
            banos_val = int(prop["bathrooms"]) if prop.get("bathrooms") else None
            area_val = int(prop["area"]) if prop.get("area") else None
        except (ValueError, TypeError):
            amb_val = None
            banos_val = None
            area_val = None

        # Verificar si ya existe (por URL)
        cursor.execute("SELECT id FROM propiedades WHERE url = ?", (prop.get("url"),))
        existe = cursor.fetchone()

        if not existe:
            # Calcular precio_por_m2 solo si tenemos área
            precio_por_m2 = None
            if area_val and area_val > 0:
                precio_por_m2 = round(precio_val / area_val, 2)

            try:
                # Insertar
                cursor.execute(
                    """
                    INSERT INTO propiedades 
                    (fecha_scraping, zona, ciudad, precio, ambientes, bathrooms, area, url, precio_por_m2)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        prop.get("fecha_scraping"),
                        prop.get("zona"),
                        prop.get("ciudad"),
                        precio_val,
                        amb_val,
                        banos_val,
                        area_val,
                        prop.get("url"),
                        precio_por_m2,
                    ),
                )
                insertados += 1
            except sqlite3.IntegrityError:
                # URL duplicada (aunque ya verificamos arriba, por si acaso)
                omitidos += 1

    conn.commit()
    conn.close()

    return insertados, omitidos


def guardar_checkpoint(zona, ciudad, pagina, db_path="../propiedades.db"):
    """
    Guarda el progreso actual en un archivo de checkpoint
    Permite reanudar el scraping desde donde se quedó
    """
    checkpoint_file = db_path.replace(".db", "_checkpoint.json")
    checkpoint = {
        "zona": zona,
        "ciudad": ciudad,
        "pagina": pagina,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint, f)


def cargar_checkpoint(db_path="../propiedades.db"):
    """
    Carga el checkpoint guardado si existe
    Retorna (zona, ciudad, pagina) o (None, None, 1) si no hay checkpoint
    """
    checkpoint_file = db_path.replace(".db", "_checkpoint.json")
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
        print(
            f"📍 Checkpoint encontrado: {checkpoint['zona']} - {checkpoint['ciudad']} - Página {checkpoint['pagina']}"
        )
        print(f"   Última actualización: {checkpoint['ultima_actualizacion']}")
        return checkpoint["zona"], checkpoint["ciudad"], checkpoint["pagina"]
    return None, None, 1


def borrar_checkpoint(db_path="../propiedades.db"):
    """Elimina el archivo de checkpoint cuando el scraping termina"""
    checkpoint_file = db_path.replace(".db", "_checkpoint.json")
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print("🗑️  Checkpoint eliminado")


def reset_scraping(db_path="../propiedades.db"):
    """
    Resetea el scraping eliminando el checkpoint
    Pregunta al usuario antes de borrar la base de datos
    """
    print("\n" + "=" * 60)
    print("🔄 REINICIANDO SCRAPING")
    print("=" * 60 + "\n")

    # Borrar checkpoint
    borrar_checkpoint(db_path)

    print("✓ Checkpoint eliminado")
    print("El scraping comenzará desde el principio.\n")


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
        url_publicacion = extraer_url(element)
        fecha_scraping = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Agregar propiedad incluso con datos parciales (igual que scraper_ml.py)
        df_data.append(
            {
                "fecha_scraping": fecha_scraping,
                "zona": zona,
                "ciudad": ciudad,
                "precio": precio,
                "ambientes": caracteristicas.get("amb") if caracteristicas else None,
                "bathrooms": caracteristicas.get("banos") if caracteristicas else None,
                "area": caracteristicas.get("m2") if caracteristicas else None,
                "url": url_publicacion,
            }
        )

    return df_data


def guardar_en_csv(df, mostrar_mensaje=True):
    df_raw = pd.DataFrame(df)
    df_raw.to_csv("./data/data.csv", index=False)
    if mostrar_mensaje:
        print("DataFrame guardado correctamente en: data.csv")


def main():
    # Verificar si hay argumento de reset
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_scraping()
        return

    todas_las_propiedades = []  # Acumular TODAS las propiedades
    total_insertados_db = 0
    total_omitidos = 0

    # Importar MAX_PAGINAS desde config
    from config import MAX_PAGINAS

    # Cargar checkpoint si existe
    checkpoint_zona, checkpoint_ciudad, checkpoint_pagina = cargar_checkpoint()
    reanudando = checkpoint_zona is not None

    if reanudando:
        print(f"\n{'=' * 60}")
        print(f"🔄 REANUDANDO SCRAPING desde el checkpoint")
        print(f"{'=' * 60}\n")
    else:
        print(f"\n{'=' * 60}")
        print(f"🚀 INICIANDO SCRAPING - Máximo {MAX_PAGINAS} páginas por ciudad")
        print(f"{'=' * 60}\n")

    # Asegurar que la tabla exista antes de empezar
    crear_tabla_si_no_existe()

    # Loop por cada zona
    for zona, ciudades in CIUDADES_POR_ZONA.items():
        # Si estamos reanudando y esta zona ya pasó, saltear
        if reanudando and zona != checkpoint_zona:
            if list(CIUDADES_POR_ZONA.keys()).index(zona) < list(
                CIUDADES_POR_ZONA.keys()
            ).index(checkpoint_zona):
                print(f"⏭️  ZONA: {zona} (ya completada)")
                continue

        print(f"\n=== ZONA: {zona} ===")

        # Loop por cada ciudad de la zona
        for ciudad in ciudades:
            # Si estamos reanudando y esta ciudad ya pasó, saltear
            if reanudando and zona == checkpoint_zona and ciudad != checkpoint_ciudad:
                if ciudades.index(ciudad) < ciudades.index(checkpoint_ciudad):
                    print(f"  ⏭️  Ciudad: {ciudad} (ya completada)")
                    continue

            print(f"\n  → Ciudad: {ciudad}")
            propiedades_ciudad = 0  # Contador para esta ciudad

            # Loop por cada página
            for pagina in range(1, MAX_PAGINAS + 1):
                # Si estamos reanudando, saltear páginas ya completadas
                if (
                    reanudando
                    and zona == checkpoint_zona
                    and ciudad == checkpoint_ciudad
                ):
                    if pagina <= checkpoint_pagina:
                        print(f"    ⏭️  Página {pagina}/{MAX_PAGINAS} (ya completada)")
                        continue
                    else:
                        # Ya pasamos el checkpoint, continuar normalmente
                        reanudando = False

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

                    # Guardar en base de datos inmediatamente
                    insertados, omitidos = guardar_en_db(propiedades)
                    total_insertados_db += insertados
                    total_omitidos += omitidos

                    mensaje = f"✓ {len(propiedades)} propiedades"
                    if insertados > 0:
                        mensaje += f" ({insertados} nuevas en DB)"
                    if omitidos > 0:
                        mensaje += f" [{omitidos} omitidas]"
                    print(mensaje)

                    # Guardar checkpoint después de cada página exitosa
                    guardar_checkpoint(zona, ciudad, pagina)

                except Exception as e:
                    print(f"✗ Error: {e}")
                    # Continuar con la siguiente página
                    continue

            print(f"    TOTAL {ciudad}: {propiedades_ciudad} propiedades")

    print(f"\n{'=' * 60}")
    print("✅ SCRAPING COMPLETADO")
    print(f"TOTAL GENERAL: {len(todas_las_propiedades)} propiedades encontradas")
    print(f"INSERTADAS EN DB: {total_insertados_db}")
    print(f"OMITIDAS: {total_omitidos}")
    print(f"{'=' * 60}\n")

    # Borrar checkpoint al finalizar exitosamente
    borrar_checkpoint()

    # Guardar versión final en CSV como backup
    if len(todas_las_propiedades) > 0:
        guardar_en_csv(todas_las_propiedades, mostrar_mensaje=True)
        print("📁 Backup CSV guardado")
    else:
        print("⚠️  No se obtuvieron nuevas propiedades")


if __name__ == "__main__":
    main()
