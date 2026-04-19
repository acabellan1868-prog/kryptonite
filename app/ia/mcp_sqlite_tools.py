"""
Herramientas de LangChain para acceder al servidor MCP SQLite
"""
import requests
from typing import Optional, Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# URL de tu servidor MCP SQLite (cambiar si es diferente)
# URL_BASE_MCP = "https://reducibly-nonguttural-julienne.ngrok-free.dev"
URL_BASE_MCP = "http://192.168.31.131:3000"


class EntradaListarTablas(BaseModel):
    """Input para listar tablas - no necesita parámetros"""
    pass


class HerramientaListarTablas(BaseTool):
    name: str = "listar_tablas_base_de_datos"
    description: str = """
    Lista todas las tablas disponibles en la base de datos de kryptonite.
    Usa esta herramienta cuando necesites saber qué datos están disponibles.
    No requiere parámetros.
    """
    args_schema: type[BaseModel] = EntradaListarTablas
    
    def _run(self) -> str:
        """Ejecuta la herramienta"""
        try:
            response = requests.get(f"{URL_BASE_MCP}/tables")
            response.raise_for_status()
            data = response.json()
            
            tables = data.get('tables', [])
            count = data.get('count', 0)
            
            return f"Base de datos contiene {count} tablas: {', '.join(tables)}"
        
        except Exception as e:
            return f"Error al listar tablas: {str(e)}"
    
    async def _arun(self) -> str:
        """Versión asíncrona"""
        return self._run()


class EntradaObtenerEsquemaTabla(BaseModel):
    """Input para obtener schema de tabla"""
    nombre_tabla: str = Field(description="Nombre de la tabla de la que obtener el schema")


class HerramientaObtenerEsquemaTabla(BaseTool):
    name: str = "obtener_esquema_tabla"
    description: str = """
    Obtiene la estructura (schema) de una tabla específica de la base de datos.
    Muestra qué columnas tiene la tabla y sus tipos de datos.
    Útil antes de hacer queries para saber qué campos están disponibles.
    """
    args_schema: type[BaseModel] = EntradaObtenerEsquemaTabla
    
    def _run(self, nombre_tabla: str) -> str:
        """Ejecuta la herramienta"""
        try:
            response = requests.get(f"{URL_BASE_MCP}/schema/{nombre_tabla}")
            response.raise_for_status()
            data = response.json()
            
            schema = data.get('schema', 'No schema available')
            
            return f"Schema de la tabla '{nombre_tabla}':\n{schema}"
        
        except Exception as e:
            return f"Error al obtener schema de '{nombre_tabla}': {str(e)}"
    
    async def _arun(self, nombre_tabla: str) -> str:
        """Versión asíncrona"""
        return self._run(nombre_tabla)


class EntradaConsultarBaseDeDatos(BaseModel):
    """Input para ejecutar queries SQL"""
    sql: str = Field(description="Query SQL SELECT a ejecutar en la base de datos")


class HerramientaConsultarBaseDeDatos(BaseTool):
    name: str = "consultar_base_de_datos"
    description: str = """
    Ejecuta una consulta SQL SELECT en la base de datos de kryptonite.
    Solo puedes usar SELECT (lectura), no INSERT/UPDATE/DELETE.
    Usa esto para obtener datos específicos de las tablas.
    Asegúrate de conocer el schema de la tabla antes de hacer la query.
    """
    args_schema: type[BaseModel] = EntradaConsultarBaseDeDatos
    
    def _run(self, sql: str) -> str:
        """Ejecuta la herramienta"""
        try:
            response = requests.post(
                f"{URL_BASE_MCP}/query",
                json={"sql": sql}
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            count = data.get('count', 0)
            
            if count == 0:
                return "La query no devolvió resultados."
            
            # Formatear resultados de forma legible
            return f"Query ejecutada exitosamente. {count} resultados:\n{str(results)}"
        
        except Exception as e:
            return f"Error al ejecutar query: {str(e)}"
    
    async def _arun(self, sql: str) -> str:
        """Versión asíncrona"""
        return self._run(sql)


class EntradaObtenerDatosTabla(BaseModel):
    """Input para obtener datos de tabla"""
    nombre_tabla: str = Field(description="Nombre de la tabla")
    limite: int = Field(default=10, description="Número de registros a obtener")


class HerramientaObtenerDatosTabla(BaseTool):
    name: str = "obtener_datos_tabla"
    description: str = """
    Obtiene una muestra de datos de una tabla específica.
    Por defecto devuelve 10 registros, pero puedes especificar más.
    Útil para ver ejemplos de datos antes de hacer queries complejas.
    """
    args_schema: type[BaseModel] = EntradaObtenerDatosTabla
    
    def _run(self, nombre_tabla: str, limite: int = 10) -> str:
        """Ejecuta la herramienta"""
        try:
            response = requests.get(
                f"{URL_BASE_MCP}/data/{nombre_tabla}",
                params={"limit": limite, "offset": 0}
            )
            response.raise_for_status()
            data = response.json()
            
            records = data.get('data', [])
            total = data.get('total', 0)
            
            return f"Tabla '{nombre_tabla}' (mostrando {len(records)} de {total} registros):\n{str(records)}"
        
        except Exception as e:
            return f"Error al obtener datos de '{nombre_tabla}': {str(e)}"
    
    async def _arun(self, nombre_tabla: str, limite: int = 10) -> str:
        """Versión asíncrona"""
        return self._run(nombre_tabla, limite)


# Lista de todas las herramientas para fácil acceso
def obtener_herramientas_mcp() -> List[BaseTool]:
    """Devuelve todas las herramientas MCP disponibles"""
    return [
        HerramientaListarTablas(),
        HerramientaObtenerEsquemaTabla(),
        HerramientaConsultarBaseDeDatos(),
        HerramientaObtenerDatosTabla()
    ]