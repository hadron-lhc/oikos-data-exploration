"""
Script de análisis exploratorio del dataset scrapeado
Genera un reporte básico para entender los datos antes de limpiarlos
"""

import pandas as pd
import sys


def cargar_datos(filepath):
    """Carga el CSV y muestra info básica"""
    print("=" * 60)
    print("CARGANDO DATOS")
    print("=" * 60)

    try:
        df = pd.read_csv(filepath)
        print(f"✓ Dataset cargado: {filepath}")
        print(f"  Filas: {len(df)}")
        print(f"  Columnas: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"✗ Error: No se encontró el archivo {filepath}")
        sys.exit(1)


def info_general(df):
    """Muestra información general del dataset"""
    print("\n" + "=" * 60)
    print("INFORMACIÓN GENERAL")
    print("=" * 60)

    print("\nColumnas y tipos:")
    print(df.dtypes)

    print("\nPrimeras 3 filas:")
    print(df.head(3))

    print("\nÚltimas 3 filas:")
    print(df.tail(3))


def analizar_nulos(df):
    """Analiza valores nulos"""
    print("\n" + "=" * 60)
    print("VALORES NULOS")
    print("=" * 60)

    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df)) * 100

    resultado = pd.DataFrame({"Nulos": nulos, "Porcentaje": porcentaje})

    print(resultado)

    if nulos.sum() > 0:
        print(f"\n⚠️  Total de valores nulos: {nulos.sum()}")
    else:
        print("\n✓ No hay valores nulos")


def estadisticas_numericas(df):
    """Estadísticas de columnas numéricas"""
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS NUMÉRICAS")
    print("=" * 60)

    # Convertir precio: el punto es separador de miles argentino

    if df["precio"].dtype == "object":
        # Quitar puntos: "198.000" → "198000"
        df["precio"] = df["precio"].str.replace(".", "", regex=False)
        df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    columnas_numericas = ["precio", "ambientes", "bathrooms", "area"]
    print(df[columnas_numericas].describe())


def distribucion_geografica(df):
    """Analiza distribución por zona y ciudad"""
    print("\n" + "=" * 60)
    print("DISTRIBUCIÓN GEOGRÁFICA")
    print("=" * 60)

    print("\nPropiedades por zona:")
    print(df["zona"].value_counts().sort_index())

    print("\n\nTop 10 ciudades con más propiedades:")
    print(df["ciudad"].value_counts().head(10))


def detectar_outliers_simples(df):
    """Detecta outliers obvios"""
    print("\n" + "=" * 60)
    print("DETECCIÓN DE OUTLIERS")
    print("=" * 60)

    # Convertir precio si es necesario
    if df["precio"].dtype == "object":
        df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    # Precios sospechosos
    precio_muy_bajo = df[df["precio"] < 10000]
    precio_muy_alto = df[df["precio"] > 1000000]

    print(f"\nPrecios < $10,000: {len(precio_muy_bajo)}")
    if len(precio_muy_bajo) > 0:
        print(precio_muy_bajo[["zona", "ciudad", "precio", "area"]].head())

    print(f"\nPrecios > $1,000,000: {len(precio_muy_alto)}")
    if len(precio_muy_alto) > 0:
        print(precio_muy_alto[["zona", "ciudad", "precio", "area"]].head())

    # Áreas sospechosas
    area_muy_pequena = df[df["area"] < 20]
    area_muy_grande = df[df["area"] > 1000]

    print(f"\nÁrea < 20 m²: {len(area_muy_pequena)}")
    print(f"Área > 1000 m²: {len(area_muy_grande)}")


def validar_urls(df):
    """Verifica que las URLs estén bien"""
    print("\n" + "=" * 60)
    print("VALIDACIÓN DE URLs")
    print("=" * 60)

    urls_nulas = df["url"].isnull().sum()
    print(f"\nURLs nulas: {urls_nulas}")

    if urls_nulas < len(df):
        print("\nMuestra de 3 URLs:")
        urls_muestra = df["url"].dropna().head(3)
        for url in urls_muestra:
            print(f"  {url}")


def main():
    # Ruta al CSV
    filepath = "../data/data.csv"

    # Cargar datos
    df = cargar_datos(filepath)

    # Análisis
    info_general(df)
    analizar_nulos(df)
    estadisticas_numericas(df)
    distribucion_geografica(df)
    detectar_outliers_simples(df)
    validar_urls(df)

    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Revisar outliers detectados")
    print("2. Decidir rangos de validación")
    print("3. Limpiar y procesar datos")
    print("4. Guardar en SQLite")


if __name__ == "__main__":
    main()
