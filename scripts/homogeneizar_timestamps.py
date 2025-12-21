#!/usr/bin/env python3
"""
Script para homogeneizar timestamps en la tabla operaciones de Kryptonite.

Convierte todos los formatos de timestamp a UNIX timestamp (INTEGER):
  - INTEGER (ya normalizado)
  - "YYYY-MM-DD HH:MM:SS" (ISO format)
  - "DD Mon YYYY, HH:MM:SS" (texto legible)

Uso:
    python3 scripts/homogeneizar_timestamps.py --dry-run  # Solo verificar
    python3 scripts/homogeneizar_timestamps.py --apply    # Aplicar cambios
"""

import sqlite3
import sys
from datetime import datetime
from typing import Union

DB_PATH = '/mnt/datos/jupyter/kryptonite/data/kryptonite.db'

# Mapeo de meses en inglés a números
MESES = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


def convertir_timestamp(timestamp_original: Union[str, int]) -> int:
    """
    Convierte cualquier formato de timestamp a UNIX timestamp (INTEGER).

    Args:
        timestamp_original: Timestamp en cualquier formato

    Returns:
        UNIX timestamp (segundos desde epoch)
    """
    # Si ya es un entero, devolverlo
    if isinstance(timestamp_original, int):
        return timestamp_original

    timestamp_str = str(timestamp_original).strip()

    # Formato 1: Ya es un número (string)
    if timestamp_str.isdigit():
        return int(timestamp_str)

    # Formato 2: ISO "YYYY-MM-DD HH:MM:SS"
    if '-' in timestamp_str and ':' in timestamp_str and ',' not in timestamp_str:
        try:
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return int(dt.timestamp())
        except ValueError as e:
            print(f"⚠️  Error parseando ISO timestamp '{timestamp_str}': {e}")
            raise

    # Formato 3: Texto legible "DD Mon YYYY, HH:MM:SS"
    if ',' in timestamp_str:
        try:
            # Ejemplo: "10 Jan 2025, 11:04:45"
            partes = timestamp_str.split(',')
            fecha_parte = partes[0].strip()  # "10 Jan 2025"
            hora_parte = partes[1].strip()    # "11:04:45"

            # Parsear fecha
            fecha_componentes = fecha_parte.split()
            dia = int(fecha_componentes[0])
            mes_texto = fecha_componentes[1]
            año = int(fecha_componentes[2])
            mes = MESES[mes_texto]

            # Parsear hora
            hora_componentes = hora_parte.split(':')
            hora = int(hora_componentes[0])
            minuto = int(hora_componentes[1])
            segundo = int(hora_componentes[2])

            # Crear datetime y convertir a timestamp
            dt = datetime(año, mes, dia, hora, minuto, segundo)
            return int(dt.timestamp())

        except (ValueError, KeyError, IndexError) as e:
            print(f"⚠️  Error parseando timestamp legible '{timestamp_str}': {e}")
            raise

    # Si llegamos aquí, formato desconocido
    raise ValueError(f"Formato de timestamp desconocido: '{timestamp_str}'")


def verificar_conversiones():
    """Verifica las conversiones sin aplicar cambios."""
    print("="*70)
    print("MODO VERIFICACIÓN - No se aplicarán cambios")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, timestamp, cripto, tipo FROM operaciones ORDER BY id")
    registros = cursor.fetchall()

    print(f"\n📊 Total de registros a procesar: {len(registros)}\n")

    errores = []
    conversiones_ok = 0

    print("ID  | Timestamp Original                | Timestamp UNIX | Fecha Legible           | Cripto | Tipo")
    print("-" * 120)

    for reg in registros:
        id_op, ts_original, cripto, tipo = reg

        try:
            ts_unix = convertir_timestamp(ts_original)
            fecha_legible = datetime.fromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S')

            print(f"{id_op:<3} | {str(ts_original):<33} | {ts_unix:<14} | {fecha_legible:<23} | {cripto:<6} | {tipo}")
            conversiones_ok += 1

        except Exception as e:
            errores.append((id_op, ts_original, str(e)))
            print(f"{id_op:<3} | {str(ts_original):<33} | ❌ ERROR: {str(e)}")

    print("\n" + "="*70)
    print(f"✅ Conversiones exitosas: {conversiones_ok}/{len(registros)}")

    if errores:
        print(f"❌ Errores encontrados: {len(errores)}")
        print("\nDetalles de errores:")
        for id_op, ts_orig, error in errores:
            print(f"  - ID {id_op}: '{ts_orig}' -> {error}")
        conn.close()
        return False
    else:
        print("✅ Todas las conversiones son correctas")
        conn.close()
        return True


def aplicar_cambios():
    """Aplica los cambios a la base de datos."""
    print("="*70)
    print("APLICANDO CAMBIOS - Creando backup primero")
    print("="*70)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Crear backup
    print("\n📦 Paso 1: Creando backup de tabla operaciones...")
    cursor.execute("DROP TABLE IF EXISTS operaciones_backup")
    cursor.execute("CREATE TABLE operaciones_backup AS SELECT * FROM operaciones")
    backup_count = cursor.execute("SELECT COUNT(*) FROM operaciones_backup").fetchone()[0]
    print(f"✅ Backup creado con {backup_count} registros")

    # 2. Obtener datos y convertir
    print("\n🔄 Paso 2: Convirtiendo timestamps...")
    cursor.execute("SELECT * FROM operaciones ORDER BY id")
    registros = cursor.fetchall()

    datos_convertidos = []
    for reg in registros:
        id_op, ts_orig, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen = reg
        ts_unix = convertir_timestamp(ts_orig)
        datos_convertidos.append((id_op, ts_unix, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen))

    print(f"✅ {len(datos_convertidos)} registros convertidos")

    # 3. Eliminar tabla original
    print("\n🗑️  Paso 3: Eliminando tabla original...")
    cursor.execute("DROP TABLE operaciones")
    print("✅ Tabla original eliminada")

    # 4. Crear nueva tabla con estructura correcta
    print("\n🏗️  Paso 4: Creando nueva tabla con timestamp INTEGER...")
    cursor.execute("""
        CREATE TABLE operaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            cripto TEXT NOT NULL,
            moneda TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cantidad REAL NOT NULL,
            precio REAL NOT NULL,
            valor_total REAL NOT NULL,
            comision REAL NOT NULL,
            origen TEXT NOT NULL
        )
    """)
    print("✅ Nueva tabla creada")

    # 5. Insertar datos convertidos
    print("\n📥 Paso 5: Insertando datos normalizados...")
    cursor.executemany("""
        INSERT INTO operaciones (id, timestamp, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos_convertidos)

    registros_insertados = cursor.execute("SELECT COUNT(*) FROM operaciones").fetchone()[0]
    print(f"✅ {registros_insertados} registros insertados")

    # 6. Commit y verificar
    conn.commit()
    print("\n💾 Paso 6: Cambios guardados en la base de datos")

    # 7. Mostrar ejemplos del resultado
    print("\n📋 Verificación final - Primeros 10 registros:")
    cursor.execute("""
        SELECT id, timestamp, datetime(timestamp, 'unixepoch') as fecha, cripto, tipo
        FROM operaciones
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    print("ID  | Timestamp UNIX | Fecha                | Cripto | Tipo")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:<3} | {row[1]:<14} | {row[2]:<20} | {row[3]:<6} | {row[4]}")

    conn.close()

    print("\n" + "="*70)
    print("✅ HOMOGENEIZACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print("\n💡 Notas:")
    print("   - Todos los timestamps ahora son INTEGER (UNIX timestamp)")
    print("   - Backup disponible en tabla: operaciones_backup")
    print("   - Para restaurar: DROP TABLE operaciones; ALTER TABLE operaciones_backup RENAME TO operaciones;")


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n❌ Error: Debes especificar --dry-run o --apply")
        sys.exit(1)

    modo = sys.argv[1]

    if modo == '--dry-run':
        if verificar_conversiones():
            print("\n✅ Verificación completada. Puedes ejecutar con --apply para aplicar cambios.")
        else:
            print("\n❌ Hay errores en las conversiones. Revisa antes de aplicar.")
            sys.exit(1)

    elif modo == '--apply':
        print("\n⚠️  ADVERTENCIA: Vas a modificar la tabla operaciones")
        print("Se creará un backup automático, pero es recomendable hacer uno manual también.")
        respuesta = input("\n¿Continuar? (escribe 'SI' para confirmar): ")

        if respuesta.strip().upper() == 'SI':
            # Primero verificar que todo esté OK
            if verificar_conversiones():
                print("\n✅ Verificación previa OK. Procediendo...")
                aplicar_cambios()
            else:
                print("\n❌ Abortado: Hay errores en las conversiones.")
                sys.exit(1)
        else:
            print("\n❌ Operación cancelada por el usuario")
            sys.exit(0)

    else:
        print(f"\n❌ Opción desconocida: {modo}")
        print("Usa --dry-run o --apply")
        sys.exit(1)


if __name__ == '__main__':
    main()