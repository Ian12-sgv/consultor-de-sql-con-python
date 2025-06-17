# logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from prometheus_client import start_http_server, Summary, Counter

# Configuración del logger
logger = logging.getLogger("ImportacionLogger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

file_handler = RotatingFileHandler("importacion.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configuración de métricas
REQUEST_TIME = Summary('importacion_request_processing_seconds', 'Tiempo de procesamiento de un bloque')
ERROR_COUNT = Counter('importacion_error_total', 'Número total de errores en la importación')

# Inicializar el servidor de métricas en el puerto 8000
start_http_server(8000)
