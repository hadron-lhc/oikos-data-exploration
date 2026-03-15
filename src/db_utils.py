"""
Utilidades para consultar la base de datos de propiedades
"""

import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "database" / "propiedades.db"

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scraper.config import CIUDADES_POR_ZONA


def obtener_zona_por_ciudad(ciudad):
    """Dado el nombre de una ciudad, devuelve la zona"""
    for zona, ciudades in CIUDADES_POR_ZONA.items():
        if ciudad in ciudades:
            return zona
    return None


def get_all_properties():
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM propiedades"

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_properties_filtered(zona=None, ciudad=None, precio_min=None, precio_max=None):
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM propiedades WHERE 1=1 "
    params = []

    if zona:
        query += "AND zona = ? "
        params.append(zona)

    if ciudad:
        query += "AND ciudad = ? "
        params.append(ciudad)

    if precio_min:
        query += "AND precio >= ? "
        params.append(precio_min)

    if precio_max:
        query += "AND precio <= ? "
        params.append(precio_max)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_unique_zones():
    """Obtiene lista de zonas únicas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT zona FROM propiedades ORDER BY zona")
    zonas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return zonas


def get_unique_cities():
    """Obtiene lista de ciudades únicas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ciudad FROM propiedades ORDER BY ciudad")
    ciudades = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ciudades


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Filtros opcionales combinados")
    print("=" * 60)

    # Test 1: Solo zona
    df1 = get_properties_filtered(zona="GBA Norte")
    print(f"\n1. Solo GBA Norte: {len(df1)} propiedades")

    # Test 2: Solo precio mínimo
    df2 = get_properties_filtered(precio_min=500000)
    print(f"2. Precio >= $500k (todas las zonas): {len(df2)} propiedades")

    # Test 3: Zona + rango de precio
    df3 = get_properties_filtered(
        zona="GBA Norte", precio_min=100000, precio_max=300000
    )
    print(f"3. GBA Norte entre $100k-$300k: {len(df3)} propiedades")

    # Test 4: Ciudad específica con precio máximo
    df4 = get_properties_filtered(ciudad="pilar", precio_max=250000)
    print(f"4. Pilar con precio <= $250k: {len(df4)} propiedades")

    # Test 5: Sin filtros (debería traer todo)
    df5 = get_properties_filtered()
    print(f"5. Sin filtros: {len(df5)} propiedades")

    # Test de listas únicas
    print("\n" + "=" * 60)
    print("Zonas disponibles:")
    for zona in get_unique_zones():
        print(f"  - {zona}")

    print(f"\nTotal ciudades: {len(get_unique_cities())}")
