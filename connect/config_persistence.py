import json
import os

# Definimos la ruta del archivo de configuración en el home del usuario.
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mi_app_last_instance_config.json")

def save_instance_config(config):
    """
    Guarda la configuración de la instancia en un archivo JSON.

    Parámetros:
        config (dict): Diccionario con la configuración de conexión. Por ejemplo:
                       {
                           "server_type": "Database Engine",
                           "server_name": "MiServidor",
                           "auth": "SQL Server Authentication",
                           "login": "mi_usuario",
                           "password": "mi_contraseña",
                           "remember": True
                       }
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        print("Configuración guardada exitosamente.")
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")

def load_instance_config():
    """
    Carga la configuración de la instancia desde el archivo JSON.

    Retorna:
        dict: La configuración guardada, o None si no existe o si ocurre algún error.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            print("Configuración cargada exitosamente.")
            return config
        except Exception as e:
            print(f"Error al cargar la configuración: {e}")
    return None
