"""
Script de limpieza y validación del dataset
Aplica filtros razonables y guarda dataset limpio
"""

import pandas as pd
import sys


def cargar_datos(filepath):
    """Carga el CSV raw"""
    print("=" * 60)
    print("CARGANDO DATOS RAW")
    print("=" * 60)

    try:
        df = pd.read_csv(filepath)
        print(f"✓ Dataset cargado: {len(df)} registros")
        return df
    except FileNotFoundError:
        print(f"✗ Error: No se encontró {filepath}")
        sys.exit(1)


def convertir_precio(df):
    """Convierte precio correctamente (quita puntos argentinos)"""
    print("\nConvirtiendo precios...")

    if df["precio"].dtype == "object":
        df["precio"] = df["precio"].str.replace(".", "", regex=False)
        df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    print("✓ Precios convertidos")
    return df


def eliminar_nulos(df):
    """Elimina registros con valores nulos en columnas críticas"""
    print("\n" + "=" * 60)
    print("ELIMINANDO NULOS")
    print("=" * 60)

    inicial = len(df)

    # Eliminar nulos en columnas críticas
    df_limpio = df.dropna(subset=["ambientes", "bathrooms", "area", "precio"])

    eliminados = inicial - len(df_limpio)
    print(f"✓ Eliminados {eliminados} registros con valores nulos")
    print(f"  Restantes: {len(df_limpio)}")

    return df_limpio


def aplicar_filtros_rangos(df):
    """Aplica filtros de rangos razonables"""
    print("\n" + "=" * 60)
    print("APLICANDO FILTROS DE RANGOS")
    print("=" * 60)

    inicial = len(df)

    # Filtros
    df_limpio = df[
        # Precio entre $20k y $2M
        (df["precio"] >= 20000)
        & (df["precio"] <= 2000000)
        &
        # Área entre 30 y 1500 m²
        (df["area"] >= 30)
        & (df["area"] <= 1500)
        &
        # Ambientes entre 1 y 10
        (df["ambientes"] >= 1)
        & (df["ambientes"] <= 10)
        &
        # Baños entre 1 y 6
        (df["bathrooms"] >= 1)
        & (df["bathrooms"] <= 6)
    ]

    eliminados = inicial - len(df_limpio)
    print(f"✓ Eliminados {eliminados} registros fuera de rangos razonables")
    print("  - Precio: $20,000 - $2,000,000 USD")
    print("  - Área: 30 - 1,500 m²")
    print("  - Ambientes: 1 - 10")
    print("  - Baños: 1 - 6")
    print(f"  Restantes: {len(df_limpio)}")

    return df_limpio


def aplicar_filtros_logica(df):
    """Aplica filtros de lógica (detectar inconsistencias)"""
    print("\n" + "=" * 60)
    print("APLICANDO FILTROS DE LÓGICA")
    print("=" * 60)

    inicial = len(df)

    # Eliminar casas muy caras con área muy pequeña (error obvio)
    df_limpio = df[~((df["precio"] > 1500000) & (df["area"] < 100))]

    # Eliminar casas muy baratas con área muy grande (sospechoso)
    df_limpio = df_limpio[~((df_limpio["precio"] < 50000) & (df_limpio["area"] > 500))]

    eliminados = inicial - len(df_limpio)
    print(f"✓ Eliminados {eliminados} registros con inconsistencias lógicas")
    print(f"  Restantes: {len(df_limpio)}")

    return df_limpio


def convertir_tipos(df):
    """Convierte columnas a tipos correctos"""
    print("\nConvirtiendo tipos de datos...")

    df["ambientes"] = df["ambientes"].astype(int)
    df["bathrooms"] = df["bathrooms"].astype(int)
    df["area"] = df["area"].astype(int)

    print("✓ Tipos convertidos")
    return df


def mostrar_estadisticas_finales(df):
    """Muestra estadísticas del dataset limpio"""
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DEL DATASET LIMPIO")
    print("=" * 60)

    print(f"\nTotal de registros: {len(df)}")

    print("\nDistribución por zona:")
    print(df["zona"].value_counts().sort_index())

    print("\nEstadísticas de precio:")
    print(f"  Mínimo: ${df['precio'].min():,.0f}")
    print(f"  Promedio: ${df['precio'].mean():,.0f}")
    print(f"  Mediana: ${df['precio'].median():,.0f}")
    print(f"  Máximo: ${df['precio'].max():,.0f}")

    print("\nEstadísticas de área:")
    print(f"  Mínimo: {df['area'].min()} m²")
    print(f"  Promedio: {df['area'].mean():.0f} m²")
    print(f"  Máximo: {df['area'].max()} m²")


def guardar_limpio(df, filepath):
    """Guarda el dataset limpio"""
    print("\n" + "=" * 60)
    print("GUARDANDO DATASET LIMPIO")
    print("=" * 60)

    df.to_csv(filepath, index=False)
    print(f"✓ Dataset limpio guardado en: {filepath}")
    print(f"  {len(df)} registros")


def main():
    # Rutas
    filepath_raw = "./data/data.csv"
    filepath_limpio = "./data/propiedades_limpias.csv"

    print("\n" + "=" * 60)
    print("PROCESO DE LIMPIEZA DE DATOS")
    print("=" * 60 + "\n")

    # 1. Cargar
    df = cargar_datos(filepath_raw)

    # 2. Convertir precio
    df = convertir_precio(df)

    # 3. Eliminar nulos
    df = eliminar_nulos(df)

    # 4. Filtros de rangos
    df = aplicar_filtros_rangos(df)

    # 5. Filtros de lógica
    df = aplicar_filtros_logica(df)

    # 6. Convertir tipos
    df = convertir_tipos(df)

    # 7. Estadísticas finales
    mostrar_estadisticas_finales(df)

    # 8. Guardar
    guardar_limpio(df, filepath_limpio)

    print("\n" + "=" * 60)
    print("LIMPIEZA COMPLETADA ✓")
    print("=" * 60)
    print("\nPróximo paso: Crear base de datos SQLite")


if __name__ == "__main__":
    main()
