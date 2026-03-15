"""
Script para crear la base de datos SQLite y cargar datos limpios
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "propiedades.db"
CSV_PATH = "./data/propiedades_limpias.csv"


def crear_database():
    """Crea la base de datos y las tablas"""
    print("=" * 60)
    print("CREANDO BASE DE DATOS")
    print("=" * 60)

    # Si existe, eliminarla (para empezar limpio)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(" Base de datos existente eliminada")

    # Conectar (esto crea el archivo)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla
    cursor.execute("""
        CREATE TABLE propiedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_scraping TEXT NOT NULL,
            zona TEXT NOT NULL,
            ciudad TEXT NOT NULL,
            precio INTEGER NOT NULL,
            ambientes INTEGER NOT NULL,
            bathrooms INTEGER NOT NULL,
            area INTEGER NOT NULL,
            url TEXT,
            precio_por_m2 REAL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print(" Tabla 'propiedades' creada")

    conn.commit()
    conn.close()

    return True


def crear_indices():
    """Crea índices para optimizar queries"""
    print("\n" + "=" * 60)
    print("CREANDO ÍNDICES")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    indices = [
        ("idx_zona", "zona"),
        ("idx_ciudad", "ciudad"),
        ("idx_precio", "precio"),
        ("idx_area", "area"),
        ("idx_precio_por_m2", "precio_por_m2"),
    ]

    for nombre_indice, columna in indices:
        cursor.execute(f"CREATE INDEX {nombre_indice} ON propiedades({columna})")
        print(f"✓ Índice '{nombre_indice}' creado en columna '{columna}'")

    conn.commit()
    conn.close()


def cargar_datos():
    """Carga los datos del CSV limpio a la base de datos"""
    print("\n" + "=" * 60)
    print("CARGANDO DATOS")
    print("=" * 60)

    # Leer CSV
    print(f"Leyendo {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"✓ {len(df)} registros leídos del CSV")

    # Calcular precio por m2
    df["precio_por_m2"] = (df["precio"] / df["area"]).round(2)
    print("✓ Precio por m² calculado")

    # Conectar a DB
    conn = sqlite3.connect(DB_PATH)

    # Insertar datos
    print("Insertando datos en la base de datos...")
    df.to_sql("propiedades", conn, if_exists="append", index=False)

    print(f"✓ {len(df)} registros insertados")

    conn.close()


def verificar_database():
    """Verifica que la base de datos se creó correctamente"""
    print("\n" + "=" * 60)
    print("VERIFICANDO BASE DE DATOS")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM propiedades")
    count = cursor.fetchone()[0]
    print(f"✓ Total de registros en DB: {count}")

    # Mostrar muestra
    print("\nMuestra de 3 registros:")
    cursor.execute(
        "SELECT id, zona, ciudad, precio, area, precio_por_m2 FROM propiedades LIMIT 3"
    )
    for row in cursor.fetchall():
        print(
            f"  ID {row[0]}: {row[1]} - {row[2]} | ${row[3]:,} | {row[4]}m² | ${row[5]}/m²"
        )

    # Estadísticas básicas
    cursor.execute("SELECT AVG(precio), MIN(precio), MAX(precio) FROM propiedades")
    avg, min_p, max_p = cursor.fetchone()
    print("\nEstadísticas de precio:")
    print(f"  Promedio: ${avg:,.0f}")
    print(f"  Mínimo: ${min_p:,}")
    print(f"  Máximo: ${max_p:,}")

    # Distribución por zona
    print("\nDistribución por zona:")
    cursor.execute(
        "SELECT zona, COUNT(*) as total FROM propiedades GROUP BY zona ORDER BY total DESC"
    )
    for zona, total in cursor.fetchall():
        print(f"  {zona}: {total} propiedades")

    conn.close()


def main():
    print("\n" + "=" * 60)
    print("CREACIÓN DE BASE DE DATOS SQLITE")
    print("=" * 60 + "\n")

    # 1. Crear database y tabla
    crear_database()

    # 2. Cargar datos
    cargar_datos()

    # 3. Crear índices (después de cargar para mejor performance)
    crear_indices()

    # 4. Verificar
    verificar_database()

    print("\n" + "=" * 60)
    print("BASE DE DATOS CREADA EXITOSAMENTE ✓")
    print("=" * 60)
    print(f"\nArchivo: {DB_PATH}")
    print(f"Tamaño: {os.path.getsize(DB_PATH) / 1024:.1f} KB")
    print("\nPróximo paso: Crear dashboard con Streamlit")


if __name__ == "__main__":
    main()
