import sys
import os

# Agregar path para importar db_utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.db_utils import get_all_properties, get_unique_zones, get_unique_cities


# Mostrar cantidad de propiedades
def mostrar_cantidad_propiedades():
    """Muestra la cantidad total de propiedades"""
    df = get_all_properties()
    print(f"Cantidad total de propiedades: {len(df):,}")


# Mostrar nombre de cada columnas
def mostrar_nombres_columnas():
    """Muestra los nombres de las columnas"""
    df = get_all_properties()
    print("Nombres de las columnas:")
    for col in df.columns:
        print(f"- {col}")


def main():
    mostrar_cantidad_propiedades()
    mostrar_nombres_columnas()


if __name__ == "__main__":
    main()
