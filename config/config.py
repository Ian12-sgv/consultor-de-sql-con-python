# config.py
CONNECTION_CONFIG = {
    'login': 'sa',
    'password': 'tu_contraseña',
    'server_name': 'MyServer\\MyInstance',
    'database': 'BODEGA_DATOS'
}

TOTAL_ROWS = 50000
BATCH_SIZE = 10000

def conectar_instancia():
    instance_name = "MiInstancia"
    return instance_name
