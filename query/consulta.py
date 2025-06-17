import pandas as pd
import time
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from functools import lru_cache
from query.sql import obtener_consulta_importacion
from contextlib import contextmanager

# Se ha eliminado toda la configuración y llamadas a logging.

@contextmanager
def disable_logs(level=None):
    """
    Context manager vacío puesto que no se realizará ninguna acción de logging.
    """
    yield

def _engine_cache_key(config: dict):
    """
    Crea una clave inmutable a partir de la configuración para cachear la conexión.
    Se asume que los campos relevantes son: server_name, database, login y password.
    """
    return (
        config.get('server_name'),
        config.get('database', "BODEGA_DATOS"),
        config.get('login'),
        config.get('password')
    )

@lru_cache(maxsize=5)
def connect_sql_cached(server_name, database, login, password):
    """
    Crea y retorna un engine de SQLAlchemy basado en los parámetros de conexión.
    Se cachea este engine para evitar recrearlo si la configuración no cambia.
    """
    driver = "SQL Server Native Client 11.0"
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server_name};"
        f"DATABASE={database};"
        f"UID={login};"
        f"PWD={password};"
        "Connection Timeout=30;"
    )
    params = quote_plus(connection_string)
    connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
    try:
        engine = create_engine(
            connection_url,
            pool_size=10,
            max_overflow=20,
            fast_executemany=True
        )
        return engine
    except Exception as e:
        return None

def connect_sql(config):
    """
    Retorna un engine de SQLAlchemy utilizando caché.
    """
    key = _engine_cache_key(config)
    engine = connect_sql_cached(*key)
    return engine

def obtener_datos(config, offset=0, limit=10000):
    """
    Ejecuta la consulta SQL con paginación y retorna un DataFrame con los datos obtenidos.
    
    Parámetros:
      config (dict): Configuración de conexión.
      offset (int): Registro inicial para la consulta.
      limit (int): Cantidad de registros a retornar.
    
    Retorna:
      DataFrame: Datos obtenidos, o uno vacío en caso de error.
    """
    engine = connect_sql(config)
    if engine is None:
        return pd.DataFrame()

    query = obtener_consulta_importacion(offset, limit)
    if not query or not query.strip():
        return pd.DataFrame()

    try:
        with disable_logs():
            inicio = time.time()
            df = pd.read_sql(query, con=engine)
            fin = time.time()
        elapsed_time = fin - inicio
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()

def obtener_datos_por_lotes(config, total_rows, batch_size=10000):
    """
    Generador que extrae datos SQL en bloques y entrega cada bloque.
    
    Parámetros:
      config (dict): Configuración de conexión.
      total_rows (int): Cantidad total de registros que se desea extraer.
      batch_size (int): Número de registros por cada bloque.
    
    Yields:
      DataFrame: Bloque de datos obtenido de la consulta.
    """
    for offset in range(0, total_rows, batch_size):
        df = obtener_datos(config, offset=offset, limit=batch_size)
        if df.empty:
            break
        yield df

if __name__ == "__main__":
    # Configuración de conexión
    config = {
        'login': 'sa',
        'password': 'tu_contraseña',
        'server_name': 'MyServer\\MyInstance',
        'database': 'BODEGA_DATOS'
    }

    total_rows = 50000
    batch_size = 10000

    bloques = []
    for df_batch in obtener_datos_por_lotes(config, total_rows, batch_size):
        bloques.append(df_batch)

    all_data = pd.concat(bloques, ignore_index=True) if bloques else pd.DataFrame()
    print("Importación completa: {} filas obtenidas.".format(len(all_data)))
