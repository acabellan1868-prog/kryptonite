-- Script para homogeneizar timestamps en la tabla operaciones
-- Convierte todos los formatos a UNIX timestamp (INTEGER)
--
-- Formatos detectados:
--   1. INTEGER (UNIX timestamp) - ej: 1760575200
--   2. ISO String (YYYY-MM-DD HH:MM:SS) - ej: "2024-11-18 10:42:26"
--   3. Texto legible (DD Mon YYYY, HH:MM:SS) - ej: "10 Jan 2025, 11:04:45"

-- ==============================================================
-- PASO 1: Crear tabla temporal con timestamps normalizados
-- ==============================================================

CREATE TABLE operaciones_temp AS
SELECT
    id,
    CASE
        -- Si ya es un número entero, mantenerlo
        WHEN timestamp LIKE '%-%' AND timestamp LIKE '%:%' AND timestamp NOT LIKE '%,%' THEN
            -- Formato ISO: "2024-11-18 10:42:26"
            CAST(strftime('%s', timestamp) AS INTEGER)

        WHEN timestamp LIKE '%,%' THEN
            -- Formato legible: "10 Jan 2025, 11:04:45"
            -- Convertir "10 Jan 2025, 11:04:45" -> "2025-01-10 11:04:45"
            CAST(strftime('%s',
                substr(timestamp, instr(timestamp, ' ', instr(timestamp, ' ') + 1) + 1, 4) || '-' ||  -- Año
                CASE substr(timestamp, instr(timestamp, ' ') + 1, 3)  -- Mes
                    WHEN 'Jan' THEN '01'
                    WHEN 'Feb' THEN '02'
                    WHEN 'Mar' THEN '03'
                    WHEN 'Apr' THEN '04'
                    WHEN 'May' THEN '05'
                    WHEN 'Jun' THEN '06'
                    WHEN 'Jul' THEN '07'
                    WHEN 'Aug' THEN '08'
                    WHEN 'Sep' THEN '09'
                    WHEN 'Oct' THEN '10'
                    WHEN 'Nov' THEN '11'
                    WHEN 'Dec' THEN '12'
                END || '-' ||
                printf('%02d', CAST(substr(timestamp, 1, instr(timestamp, ' ') - 1) AS INTEGER)) || ' ' ||  -- Día
                substr(timestamp, instr(timestamp, ',') + 2)  -- Hora
            ) AS INTEGER)

        ELSE
            -- Ya es INTEGER (UNIX timestamp)
            CAST(timestamp AS INTEGER)
    END AS timestamp_normalizado,
    timestamp AS timestamp_original,
    cripto,
    moneda,
    tipo,
    cantidad,
    precio,
    valor_total,
    comision,
    origen
FROM operaciones;

-- ==============================================================
-- PASO 2: Verificar conversiones antes de aplicar cambios
-- ==============================================================

-- Mostrar ejemplos de conversión para revisar
SELECT
    id,
    timestamp_original,
    timestamp_normalizado,
    datetime(timestamp_normalizado, 'unixepoch') AS fecha_legible
FROM operaciones_temp
ORDER BY id
LIMIT 10;

-- Verificar si hay NULLs o conversiones fallidas
SELECT COUNT(*) as registros_con_error
FROM operaciones_temp
WHERE timestamp_normalizado IS NULL;

-- ==============================================================
-- PASO 3: Aplicar cambios (DESCOMENTAR CUANDO ESTÉ VERIFICADO)
-- ==============================================================

-- IMPORTANTE: Ejecutar estos pasos solo después de verificar que
-- las conversiones son correctas en el PASO 2

-- Crear backup de la tabla original
-- CREATE TABLE operaciones_backup AS SELECT * FROM operaciones;

-- Eliminar tabla original
-- DROP TABLE operaciones;

-- Renombrar tabla temporal
-- ALTER TABLE operaciones_temp RENAME TO operaciones_temp2;

-- Crear tabla con estructura correcta (timestamp como INTEGER)
-- CREATE TABLE operaciones (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     timestamp INTEGER NOT NULL,
--     cripto TEXT NOT NULL,
--     moneda TEXT NOT NULL,
--     tipo TEXT NOT NULL,
--     cantidad REAL NOT NULL,
--     precio REAL NOT NULL,
--     valor_total REAL NOT NULL,
--     comision REAL NOT NULL,
--     origen TEXT NOT NULL
-- );

-- Insertar datos normalizados
-- INSERT INTO operaciones (id, timestamp, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen)
-- SELECT id, timestamp_normalizado, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen
-- FROM operaciones_temp2;

-- Limpiar tabla temporal
-- DROP TABLE operaciones_temp2;

-- Opcional: Verificar resultado final
-- SELECT
--     id,
--     timestamp,
--     datetime(timestamp, 'unixepoch') AS fecha_legible,
--     cripto,
--     tipo,
--     cantidad
-- FROM operaciones
-- ORDER BY timestamp DESC
-- LIMIT 10;
