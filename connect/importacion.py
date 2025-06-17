import sys
import os
# Ajuste del sys.path para incluir el directorio raíz
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import time
import pandas as pd
import duckdb
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from config.logging_config import logger, REQUEST_TIME, ERROR_COUNT
from query.sql import obtener_consulta_importacion  # Se importa la función que genera la consulta completa

def obtener_datos(config, offset, limit):
    """
    Ejecuta la consulta SQL obtenida dinámicamente (desde query/sql.py) a la cual se añade
    la cláusula de paginación y devuelve el DataFrame resultante.
    La configuración se utiliza para establecer una conexión a la base de datos.
    
    Parámetros:
      config (dict): Diccionario de configuración que debe incluir al menos el parámetro 'database'
                     indicando la ruta o el nombre de la base de datos (ej: 'mi_base.duckdb' o ":memory:").
      offset (int): Número de filas a saltar.
      limit (int): Número de filas a retornar.
      
    Retorna:
      DataFrame: El DataFrame obtenido de ejecutar la consulta.
                En caso de error o consulta vacía, retorna un DataFrame vacío.
    """
    # Se obtiene la consulta ya preparada
    consulta = obtener_consulta_importacion(offset, limit)
    
    # Verificar que la consulta no esté vacía
    if not consulta.strip():
        logger.error("La consulta SQL generada está vacía.")
        return pd.DataFrame()
    
    logger.debug(f"Ejecutando consulta SQL con OFFSET {offset} y LIMIT {limit}:\n{consulta}")
    
    # Extraer la ruta de la base de datos de la configuración; si no se indica, se usa ":memory:"
    db_path = config.get("database", ":memory:")
    
    try:
        # Conectarse a la base de datos; se elimina read_only para permitir la creación si es necesario.
        with duckdb.connect(database=db_path) as con:
            df = con.execute(consulta).fetchdf()
        return df
    except Exception as e:
        logger.error(f"Error ejecutando la consulta SQL: {e}", exc_info=True)
        return pd.DataFrame()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def obtener_datos_con_reintento(config, offset, limit):
    df = obtener_datos(config, offset, limit)
    if df.empty:
        raise ValueError("No se obtuvo data o está vacía")
    return df

def importar_datos_generator(config, total_rows, batch_size):
    """
    Generador que devuelve datos en bloques (offset, DataFrame) usando la consulta dinámica.
    Se aplican reintentos para cada bloque para asegurar que, aunque la consulta no devuelva
    resultados, se intente nuevamente.
    """
    for offset in range(0, total_rows, batch_size):
        try:
            inicio = time.time()
            df = obtener_datos_con_reintento(config, offset, batch_size)
            fin = time.time()
            logger.info(f"Bloque OFFSET {offset} importado en {fin - inicio:.2f} segundos.")
            yield offset, df
        except RetryError as re:
            ERROR_COUNT.inc()
            logger.error(f"Error en OFFSET {offset} tras varios intentos: {re}")
            continue
        except Exception as e:
            ERROR_COUNT.inc()
            logger.error(f"Error inesperado en OFFSET {offset}: {e}", exc_info=True)
            continue

def importar_datos_con_metricas(config, total_rows=50000, batch_size=10000):
    """
    Ejecuta la consulta dinámica de forma paginada y concatena todos los bloques en un único DataFrame.
    Así, cualquier cambio en el SQL se refleja automáticamente en los datos extraídos.
    """
    bloques = []
    for offset in range(0, total_rows, batch_size):
        try:
            inicio = time.time()
            df = obtener_datos_con_reintento(config, offset, batch_size)
            fin = time.time()
            logger.info(f"Bloque OFFSET {offset} importado en {fin - inicio:.2f} segundos.")
            bloques.append(df)
        except RetryError as re:
            ERROR_COUNT.inc()
            logger.error(f"Error en OFFSET {offset} tras varios intentos: {re}")
            continue
        except Exception as e:
            ERROR_COUNT.inc()
            logger.error(f"Error inesperado en OFFSET {offset}: {e}", exc_info=True)
            continue
    return pd.concat(bloques, ignore_index=True) if bloques else pd.DataFrame()

def exportar_a_parquet(dataframe, filename="datos.parquet"):
    """
    Exporta el DataFrame a un archivo Parquet y retorna su nombre,
    o None si ocurre algún error.
    """
    try:
        dataframe.to_parquet(filename, index=False)
        logger.info("Exportación a Parquet completada.")
        return filename
    except Exception as e:
        logger.error(f"Error al exportar a Parquet: {e}", exc_info=True)
        return None

def consulta_con_duckdb(parquet_file, exist_threshold=0):
    """
    Ejecuta una consulta analítica con DuckDB sobre el archivo Parquet.
    """
    query = f"""
        SELECT *
        FROM '{parquet_file}'
        WHERE Existencia > {exist_threshold}
    """
    try:
        result_df = duckdb.query(query).to_df()
        logger.info("Consulta con DuckDB ejecutada correctamente.")
        return result_df
    except Exception as e:
        logger.error(f"Error en la consulta con DuckDB: {e}", exc_info=True)
        return pd.DataFrame()

def conectar_instancia():
    """
    Simula la conexión a una instancia y retorna un nombre de instancia.
    """
    instance_name = "MiInstancia"
    logger.info(f"Conectado a la instancia: {instance_name}")
    return instance_name

# -------------------------------
# Ejemplo de Uso (modo consola)
# -------------------------------
if __name__ == "__main__":
    try:
        config = {
            'login': 'sa',
            'password': 'tu_contraseña',
            'server_name': 'MyServer\\MyInstance',
            # Asegúrate de que 'database' sea la ruta correcta a tu archivo DuckDB o ":memory:" si trabajas en memoria.
            'database': 'BODEGA_DATOS'
        }
        
        instancia = conectar_instancia()
        
        # Importación completa de datos
        df_importado = importar_datos_con_metricas(config, total_rows=50000, batch_size=10000)
        logger.info("Importación completa. Mostrando algunas filas:")
        print(df_importado.head())
        
        # Exportar a Parquet y ejecutar consulta analítica
        parquet_file = exportar_a_parquet(df_importado, filename="datos.parquet")
        if parquet_file:
            result_df = consulta_con_duckdb(parquet_file, exist_threshold=0)
            logger.info("Resultados de la consulta:")
            print(result_df.head())
        
        # Uso del generador para procesar bloques incrementalmente
        logger.info("Uso del generador para procesar bloques:")
        for offset, df in importar_datos_generator(config, total_rows=50000, batch_size=10000):
            logger.info(f"Lote recibido mediante generador: OFFSET {offset}")
    except Exception as e:
        logger.exception("Error principal durante la importación de datos:")
        print(f"Error: {e}")
