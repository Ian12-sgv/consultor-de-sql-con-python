# consulta.py
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from .sql import obtener_consulta_importacion  # Importamos la consulta desde sql.py

def connect_sql(config):
    """
    Crea y retorna un engine de SQLAlchemy para conectarse a SQL Server.

    Parámetros en config:
      - login: Nombre de usuario.
      - password: Contraseña.
      - server_name: Nombre del servidor y la instancia en el formato 'SERVIDOR\\INSTANCIA'
      - database: (Opcional) Nombre de la base de datos (por defecto 'BODEGA_DATOS').
    """
    password_enc = quote_plus(config['password'])
    database = config.get("database", "BODEGA_DATOS")
    connection_str = (
        f"mssql+pyodbc://{config['login']}:{password_enc}@{config['server_name']}/{database}?driver=SQL+Server"
    )
    try:
        engine = create_engine(connection_str, pool_size=10, max_overflow=20)
        return engine
    except Exception as e:
        print(f"Error al crear el engine: {e}")
        return None

def obtener_datos(config):
    """
    Ejecuta la consulta SQL definida en sql.py utilizando el engine creado con la configuración dada
    y retorna un DataFrame.
    """
    engine = connect_sql(config)
    if engine is None:
        return pd.DataFrame()
    
    # Importamos la consulta de sql.py
    query = obtener_consulta_importacion()

    try:
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Ejemplo de configuración de conexión
    config = {
        'login': 'sa',
        'password': 'tu_contraseña',
        'server_name': 'MyServer\\MyInstance',
        'database': 'BODEGA_DATOS'
    }
    
    # Conectar y ejecutar la consulta para obtener datos
    engine = connect_sql(config)
    
    if engine:
        df = obtener_datos(config)
        print("Datos obtenidos:")
        print(df.head())
    else:
        print("No se pudo establecer la conexión.")
