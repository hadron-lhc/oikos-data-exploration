"""
Script para ver estadísticas de la base de datos
"""

import sqlite3
import pandas as pd

DB_PATH = "propiedades.db"


def mostrar_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 60)

    # Total de propiedades
    cursor.execute("SELECT COUNT(*) FROM propiedades")
    total = cursor.fetchone()[0]
    print(f"\n📊 TOTAL DE PROPIEDADES: {total:,}")

    # Por zona
    print("\n" + "=" * 60)
    print("PROPIEDADES POR ZONA")
    print("=" * 60)
    cursor.execute("""
        SELECT zona, COUNT(*) as cantidad 
        FROM propiedades 
        GROUP BY zona 
        ORDER BY cantidad DESC
    """)
    for zona, cantidad in cursor.fetchall():
        print(f"{zona:25} {cantidad:,} propiedades")

    # Top 10 ciudades
    print("\n" + "=" * 60)
    print("TOP 10 CIUDADES")
    print("=" * 60)
    cursor.execute("""
        SELECT ciudad, zona, COUNT(*) as cantidad 
        FROM propiedades 
        GROUP BY ciudad, zona 
        ORDER BY cantidad DESC 
        LIMIT 10
    """)
    for ciudad, zona, cantidad in cursor.fetchall():
        print(f"{ciudad:20} ({zona:20}) {cantidad:,} propiedades")

    # Estadísticas de precio
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE PRECIO")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            MIN(precio) as min_precio,
            AVG(precio) as avg_precio,
            MAX(precio) as max_precio
        FROM propiedades
    """)
    min_p, avg_p, max_p = cursor.fetchone()
    print(f"Mínimo:   ${min_p:>12,}")
    print(f"Promedio: ${avg_p:>12,.0f}")
    print(f"Máximo:   ${max_p:>12,}")

    # Estadísticas de área
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE ÁREA")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            MIN(area) as min_area,
            AVG(area) as avg_area,
            MAX(area) as max_area
        FROM propiedades
    """)
    min_a, avg_a, max_a = cursor.fetchone()
    print(f"Mínimo:   {min_a:>8.0f} m²")
    print(f"Promedio: {avg_a:>8.0f} m²")
    print(f"Máximo:   {max_a:>8.0f} m²")

    # Precio por m² promedio por zona
    print("\n" + "=" * 60)
    print("PRECIO POR M² PROMEDIO POR ZONA")
    print("=" * 60)
    cursor.execute("""
        SELECT zona, AVG(precio_por_m2) as avg_precio_m2
        FROM propiedades
        WHERE precio_por_m2 IS NOT NULL
        GROUP BY zona
        ORDER BY avg_precio_m2 DESC
    """)
    for zona, avg_pm2 in cursor.fetchall():
        print(f"{zona:25} ${avg_pm2:>10,.0f}/m²")

    # Fechas de scraping
    print("\n" + "=" * 60)
    print("FECHAS DE SCRAPING")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            MIN(fecha_scraping) as primera,
            MAX(fecha_scraping) as ultima,
            COUNT(DISTINCT fecha_scraping) as dias_diferentes
        FROM propiedades
    """)
    primera, ultima, dias = cursor.fetchone()
    print(f"Primera:  {primera}")
    print(f"Última:   {ultima}")
    print(f"Días diferentes: {dias}")

    conn.close()


if __name__ == "__main__":
    mostrar_stats()
