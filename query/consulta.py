# query/consulta.py
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from .sql import obtener_consulta_importacion

def connect_sql(config):
    """
    Crea y retorna un engine de SQLAlchemy para conectarse a SQL Server utilizando odbc_connect.
    
    Parámetros en config:
      - login: Nombre de usuario.
      - password: Contraseña.
      - server_name: Nombre del servidor y la instancia en formato 'SERVIDOR\\INSTANCIA'.
      - database: (Opcional) Nombre de la base de datos (por defecto 'BODEGA_DATOS').
    """
    driver = "SQL Server Native Client 11.0"  # Asegúrate de que este nombre coincide con el driver instalado
    server = config['server_name']
    database = config.get("database", "BODEGA_DATOS")
    username = config['login']
    password = config['password']
    
    # Forma completa de la cadena de conexión para ODBC
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Connection Timeout=30;"
    )
    
    # URL-encode de la cadena de conexión
    params = quote_plus(connection_string)
    # Construir la URL usando odbc_connect
    connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
    
    try:
        engine = create_engine(connection_url, pool_size=10, max_overflow=20)
        return engine
    except Exception as e:
        print(f"Error al crear el engine: {e}")
        return None

def obtener_datos(config, offset=None, limit=None):
    """
    Ejecuta la consulta SQL definida en sql.py utilizando el engine creado con la configuración dada
    y retorna un DataFrame.
    
    Parámetros:
      config (dict): Diccionario con la configuración de conexión.
      offset (int, opcional): Número de filas a saltar (para paginación).
      limit (int, opcional): Número máximo de filas a retornar (para paginación).
    
    Retorna:
      DataFrame con los datos importados. Si ocurre un error, retorna un DataFrame vacío.
    
    Nota:
      Para la paginación se asume que la consulta SQL incluye un ORDER BY.
    """
    engine = connect_sql(config)
    if engine is None:
        return pd.DataFrame()
    
    query = obtener_consulta_importacion()
    
    # Si se especifican valores para paginación, modifica la query
    if offset is not None and limit is not None:
        query += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
    
    try:
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Configuración de ejemplo
    config = {
        'login': 'sa',
        'password': 'tu_contraseña',
        'server_name': 'MyServer\\MyInstance',
        'database': 'BODEGA_DATOS'
    }
    
    # Ejemplo: obtener los primeros 10,000 registros
    df = obtener_datos(config, offset=0, limit=10000)
    print("Datos obtenidos:")
    print(df.head())
