"""
Limpia la base de datos eliminando outliers y datos inválidos
"""

import sqlite3

DB_PATH = "../propiedades.db"


def limpiar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("LIMPIANDO BASE DE DATOS")
    print("=" * 60)

    # Contar registros antes
    cursor.execute("SELECT COUNT(*) FROM propiedades")
    total_antes = cursor.fetchone()[0]
    print(f"\nRegistros antes de limpiar: {total_antes:,}")

    # Eliminar registros con datos inválidos
    print("\nEliminando registros inválidos...")

    cursor.execute("""
        DELETE FROM propiedades
        WHERE 
            precio < 20000 OR precio > 2000000
            OR area < 30 OR area > 1500
            OR ambientes < 1 OR ambientes > 10
            OR bathrooms < 1 OR bathrooms > 6
            OR precio IS NULL
            OR area IS NULL
            OR ambientes IS NULL
            OR bathrooms IS NULL
    """)

    eliminados = cursor.rowcount
    print(f"✓ Eliminados {eliminados:,} registros inválidos")

    # Contar registros después
    cursor.execute("SELECT COUNT(*) FROM propiedades")
    total_despues = cursor.fetchone()[0]

    print(f"\n{'=' * 60}")
    print(f"RESUMEN")
    print(f"{'=' * 60}")
    print(f"Antes:     {total_antes:,}")
    print(f"Después:   {total_despues:,}")
    print(f"Eliminados: {eliminados:,} ({(eliminados / total_antes) * 100:.1f}%)")

    conn.commit()

    # Recalcular precio_por_m2 para asegurar consistencia
    print(f"\nRecalculando precio_por_m2...")
    cursor.execute("""
        UPDATE propiedades
        SET precio_por_m2 = ROUND(CAST(precio AS REAL) / CAST(area AS REAL), 2)
        WHERE area > 0
    """)
    print(f"✓ Precio por m² actualizado")

    conn.commit()
    conn.close()

    print(f"\n✅ Limpieza completada")


if __name__ == "__main__":
    respuesta = input(
        "¿Estás seguro de limpiar la DB? Esto eliminará datos permanentemente. (si/no): "
    )
    if respuesta.lower() == "si":
        limpiar_db()
    else:
        print("Operación cancelada")
