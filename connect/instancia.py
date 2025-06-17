# instancia_logic.py
import subprocess
import os
from sqlalchemy import text
from urllib.parse import quote_plus

# Importa el módulo de conexión.
from connect import db as connection

def get_current_instance(engine):
    """
    Retorna el nombre de la instancia a la que se está conectado utilizando @@SERVERNAME.
    """
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@SERVERNAME AS servername")).fetchone()
        if result is not None:
            result_dict = dict(result._mapping)
            return result_dict.get("servername")
    return None

def get_available_sql_servers():
    """
    Utiliza la utilidad sqlcmd para listar instancias de SQL Server disponibles en la red.
    
    Retorna:
      - Una lista de cadenas con los nombres de las instancias detectadas.
    
    Nota: sqlcmd debe estar instalado y en el PATH del sistema.
    """
    try:
        result = subprocess.run(
            ['sqlcmd', '-L'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Se omite la cabecera "Servers:" y se filtran líneas vacías.
        instancias = [
            line.strip() for line in output.splitlines()
            if line.strip() and not line.lower().startswith('servers')
        ]
        return instancias
    except Exception as e:
        return []

def get_default_username():
    """
    Retorna el nombre de usuario por defecto, intentando usar el usuario del sistema.
    """
    try:
        return os.getlogin()
    except Exception:
        return "default_user"

def set_connection_config(config):
    """
    Configura la conexión llamando a connection.set_default_instance().
    """
    connection.set_default_instance(config)

def load_connection_config():
    """
    Carga la configuración de conexión previamente guardada utilizando el módulo de persistencia.
    
    Retorna:
      - Un diccionario con la configuración guardada, o None si no existe.
    """
    from connect.config_persistence import load_instance_config
    config = load_instance_config()
    return config

def save_connection_config(config):
    """
    Guarda la configuración de conexión utilizando el módulo de persistencia,
    siempre que la opción 'remember' esté activada en el diccionario de configuración.
    """
    from connect.config_persistence import save_instance_config
    if config.get("remember"):
        save_instance_config(config)
