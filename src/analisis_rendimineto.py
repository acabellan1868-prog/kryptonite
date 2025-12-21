import sqlite3
# Importamos la función específica para obtener operaciones y la de obtener portafolio
from config import logger, FAVORITES_FILTER, DB_PATH
# Importamos las funciones necesarias de database y la clase CriptoEnCartera
from database import obtener_portafolio # obtener_operaciones_por_criptomoneda ya no es necesaria aquí directamente
from modelos import CriptoEnCartera # Importar la clase CriptoEnCartera

def calcular_rendimiento_criptomoneda(simbolo_criptomoneda: str):
    """
    Calcula el rendimiento (beneficio/pérdida) para una criptomoneda específica.
    Args:
        simbolo_criptomoneda: El símbolo de la criptomoneda (ej. 'BTC', 'ETH').
    """
    logger.info(f"Calculando rendimiento detallado para {simbolo_criptomoneda}...")

    try:
        # 1. Utilizar CriptoEnCartera para obtener los datos consolidados
        # La clase CriptoEnCartera internamente llama a database.calcular_posicion_actual
        # que a su vez lee de la tabla 'operaciones' para obtener cantidad y coste.
        cripto = CriptoEnCartera(simbolo_criptomoneda)

        # Accedemos a las propiedades de CriptoEnCartera.
        # Estas propiedades tienen su propia lógica de caché y obtención de datos.
        cantidad_actual = cripto.cantidad_total
        
        # Si no hay cantidad, significa que no hay tenencias o no hay operaciones.
        # Usamos <= 0 para cubrir el caso de 0 exacto o pequeños residuales negativos si fuera posible.
        if cantidad_actual <= 0:
            logger.info(f"No hay tenencias actuales para {simbolo_criptomoneda} o no hay operaciones registradas.")
            return {
                "simbolo": simbolo_criptomoneda,
                "cantidad_actual": 0.0,
                "precio_medio_compra": 0.0,
                "coste_total_inversion": 0.0,
                "precio_actual": cripto.precio_actual, # Puede tener precio aunque no haya tenencias
                "valor_actual_inversion": 0.0,
                "ganancia_perdida_abs": 0.0,
                "rentabilidad_porcentaje": 0.0
            }

        # Obtenemos el coste total de la inversión y el precio medio de compra de las tenencias actuales.
        # Estos valores ya están calculados por CriptoEnCartera basándose en la tabla 'operaciones'.
        coste_total_inversion = cripto.coste_total_inversion
        precio_medio_compra = cripto.precio_medio_compra # coste_total_inversion / cantidad_total

        # Obtenemos el precio actual de mercado y el valor actual de la inversión.
        precio_actual = cripto.precio_actual
        valor_actual_inversion = cripto.valor_actual_inversion # precio_actual * cantidad_total

        # La rentabilidad porcentual ya la calcula CriptoEnCartera.
        rentabilidad_porcentaje = cripto.rentabilidad 
        
        # Calculamos la ganancia o pérdida absoluta.
        ganancia_perdida_abs = valor_actual_inversion - coste_total_inversion

        # Preparamos el diccionario de resultados con nombres de claves consistentes.
        datos_rendimiento = {
            "simbolo": simbolo_criptomoneda,
            "cantidad_actual": round(cantidad_actual, 8),
            "precio_medio_compra": round(precio_medio_compra, 8),
            "coste_total_inversion": round(coste_total_inversion, 2),
            "precio_actual": round(precio_actual, 8),
            "valor_actual_inversion": round(valor_actual_inversion, 2),
            "ganancia_perdida_abs": round(ganancia_perdida_abs, 2),
            "rentabilidad_porcentaje": round(rentabilidad_porcentaje, 2)
        }
        logger.info(f"Análisis de {simbolo_criptomoneda}: {datos_rendimiento}")
        return datos_rendimiento

    except Exception as e:
        logger.error(f"Error al calcular rendimiento para {simbolo_criptomoneda}: {e}", exc_info=True)
        # Retornar un diccionario con valores por defecto en caso de error
        return {
            "simbolo": simbolo_criptomoneda,
            "cantidad_actual": 0.0,
            "precio_medio_compra": 0.0,
            "coste_total_inversion": 0.0,
            # Intentar obtener el precio actual incluso en error, si es posible, o default a 0
            "precio_actual": CriptoEnCartera(simbolo_criptomoneda).precio_actual if 'cripto' not in locals() else cripto.precio_actual,
            "valor_actual_inversion": 0.0,
            "ganancia_perdida_abs": 0.0,
            "rentabilidad_porcentaje": 0.0
        }



def calcular_rendimiento_portafolio_total():
    """
    Calcula el rendimiento para todas las criptomonedas marcadas en el portafolio.
    """
    simbolos_del_portafolio  = obtener_portafolio() # ['BTC', 'ETH', ...]
    lista_resultados_completos = []

    if simbolos_del_portafolio  is None:
        logger.error("No se pudo obtener la lista de criptomonedas del portafolio.")
        return []
    if not simbolos_del_portafolio :
        logger.info("No hay criptomonedas marcadas en el portafolio.")
        return []

    for simbolo in simbolos_del_portafolio :
        logger.info(f"Calculando rendimiento para {simbolo}...")
        rendimiento_de_criptomoneda = calcular_rendimiento_criptomoneda(simbolo)
        if rendimiento_de_criptomoneda:
            lista_resultados_completos.append(rendimiento_de_criptomoneda)
    
    return lista_resultados_completos

if __name__ == "__main__":
    resultados_finales = calcular_rendimiento_portafolio_total()
    print("\n--- Resultados del Rendimiento del Portafolio ---")
    for resultado_cripto in resultados_finales:
        print(resultado_cripto)