# connect/db.py
import subprocess
import re
import pandas as pd
from sqlalchemy import create_engine
from tkinter import messagebox
from urllib.parse import quote_plus

# Variable global para el connection string
DEFAULT_CONNECTION_STR = None

def set_default_instance(config):
    """
    Configura la cadena de conexión a partir del diccionario 'config'.
    
    Parámetros esperados:
      - login: Usuario de acceso a la base de datos.
      - password: Contraseña del usuario.
      - server_name: Nombre del servidor o instancia.
      
    Ejemplo:
      config = {
          'login': 'sa',
          'password': 'tu_contraseña',
          'server_name': 'SERVIDOR\\INSTANCIA'  # Por ejemplo: 'SERVERDOS\\SERVERSQL_DOS'
      }
    """
    global DEFAULT_CONNECTION_STR
    password_enc = quote_plus(config['password'])
    # Se fija la base de datos en 'BODEGA_DATOS'
    DEFAULT_CONNECTION_STR = (
        f"mssql+pyodbc://{config['login']}:{password_enc}@{config['server_name']}/BODEGA_DATOS?driver=SQL+Server"
    )

def get_db_connection(connection_str=None):
    """
    Retorna una instancia de engine para la conexión a la base de datos.
    Se configuran los parámetros del pool de conexiones (pool_size y max_overflow).
    """
    try:
        connection_str = connection_str or DEFAULT_CONNECTION_STR
        if not connection_str:
            raise ValueError("No se ha configurado el connection string.")
        return create_engine(connection_str, pool_size=10, max_overflow=20)
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo crear el engine: {e}")
        return None

def listar_instancias_sql():
    """
    Utiliza la utilidad sqlcmd para listar las instancias de SQL Server disponibles en la red.
    
    Retorna:
      - Una lista de cadenas (strings) con los nombres de las instancias detectadas.
      
    Nota: sqlcmd debe estar instalado y en el PATH del sistema.
    """
    try:
        # Ejecuta el comando `sqlcmd -L` y captura la salida
        result = subprocess.run(['sqlcmd', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        # El comando sqlcmd suele devolver:
        # "Servers:\n\tSERVIDOR1\n\tSERVIDOR2\\INSTANCIA\n\n"
        # Se filtran las líneas que no sean vacías ni la cabecera.
        instancias = [line.strip() for line in output.splitlines() 
                      if line.strip() and not line.lower().startswith('servers')]
        return instancias
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo listar instancias de SQL Server: {e}")
        return []

# Ejemplo de uso en consola (para pruebas)
if __name__ == "__main__":
    servidores = listar_instancias_sql()
    print("Instancias SQL detectadas en la red:")
    for s in servidores:
        print(s)
