import re
import pandas as pd


def procesar_caracteristicas(caracteristicas_raw):
    """
    Convierte ['9 dormitorios', '6 baños', '400 m² cubiertos']
    a {'dormitorios': 9, 'banos': 6, 'm2': 400}
    """
    resultado = {"amb": None, "banos": None, "m2": None}

    if not caracteristicas_raw:
        return resultado

    for item in caracteristicas_raw:
        # Extraer el número (uno o más dígitos)
        numeros = re.findall(r"\d+", item)
        if not numeros:
            continue

        numero = int(numeros[0])
        texto_lower = item.lower()

        # Identificar qué tipo de dato es
        if "dorm" in texto_lower or "amb" in texto_lower:
            resultado["amb"] = numero
        elif "baño" in texto_lower:
            resultado["banos"] = numero
        elif "m²" in texto_lower or "m2" in texto_lower:
            resultado["m2"] = numero

    return resultado


def leer_datos(filename):
    """Lee el CSV y retorna un DataFrame"""
    return pd.read_csv(filename)


def validar_datos(df):
    """Elimina filas con datos sospechosos"""
    """
    Elimina filas con datos fuera de rangos razonables
    """
    print(f"Filas antes de validar: {len(df)}")

    df["precio"] = pd.to_numeric(df["precio"], errors="coerce") * 1000

    # Filtrar por rangos razonables
    df_valido = df[
        # Área entre 20 y 1000 m²
        (df["area"] >= 20)
        & (df["area"] <= 1000)
        &
        # Ambientes entre 1 y 10
        (df["ambientes"] >= 1)
        & (df["ambientes"] <= 10)
        &
        # Baños entre 1 y 6
        (df["bathrooms"] >= 1)
        & (df["bathrooms"] <= 6)
        # Precio mayor a 10,000 dólares
        & (df["precio"] >= 10000)
    ]

    print(f"Filas después de validar: {len(df_valido)}")
    print(f"Filas eliminadas: {len(df) - len(df_valido)}")

    return df_valido


def guardar_datos_limpios(df, filename):
    """Guarda el DataFrame limpio en CSV"""
    df.to_csv(filename, index=False)


def convertir_tipos(df):
    """Convierte las columnas a sus tipos de datos correctos"""

    # Convertir precio a float (ya está multiplicado por 1000)
    df["precio"] = df["precio"].astype(float)

    # Convertir ambientes a int
    df["ambientes"] = df["ambientes"].astype(int)

    # Convertir baños a int
    df["bathrooms"] = df["bathrooms"].astype(int)

    # Convertir área (depende si querés decimales o no)
    df["area"] = df["area"].astype(int)  # Sin decimales
    # O:
    # df['area'] = df['area'].astype(float)  # Con decimales

    return df


def renombrar_columnas(df):
    """Renombra columnas a inglés"""
    df = df.rename(
        columns={
            "zona": "zone",
            "ciudad": "city",
            "precio": "price",
            "ambientes": "rooms",
            "bathrooms": "bathrooms",  # Ya está en inglés
            "area": "area",  # Ya está en inglés
        }
    )
    return df


def main():
    # Leer datos
    df = leer_datos("./data.csv")

    print("=== TIPOS ANTES ===")
    print(df.dtypes)

    # Validar (esto ya filtra filas malas)
    df_limpio = validar_datos(df)

    # Eliminar filas con nulos en columnas críticas
    df_limpio = df_limpio.dropna(subset=["ambientes", "bathrooms", "area", "precio"])

    # Convertir tipos
    df_limpio = convertir_tipos(df_limpio)

    df_limpio = renombrar_columnas(df_limpio)

    print("\n=== TIPOS DESPUÉS ===")
    print(df_limpio.dtypes)

    print("\n=== MUESTRA DE DATOS ===")
    print(df_limpio.head())

    # Guardar
    guardar_datos_limpios(df_limpio, "propiedades_limpias.csv")


if __name__ == "__main__":
    main()
