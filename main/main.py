import sys
import os
from PyQt5.QtWidgets import QApplication

def setup_paths():
    """
    Ajusta el path para incluir el directorio padre.
    En proyectos reales, se recomienda configurar el ambiente o usar un archivo de configuración.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Ejecutamos el ajuste de paths antes de los imports de paquetes
setup_paths()

# Importamos desde los paquetes correspondientes
from view.instanciaUI import get_connection_config
from connect.instancia import get_current_instance
from connect.db import set_default_instance, get_db_connection
from view.viewImport import ImportWindow

# También importamos la configuración por defecto y la función de conexión simulada  
from config.config import CONNECTION_CONFIG, conectar_instancia

def main():
    """
    Función principal que inicia la aplicación:
      - Ajusta los paths de búsqueda.
      - Obtiene la configuración de conexión (usando get_connection_config o la predeterminada).
      - Configura la instancia de conexión y obtiene el engine.
      - Recupera el nombre de la instancia actual (usando la conexión real o una simulación).
      - Lanza la ventana de importación de datos.
    """
    app = QApplication(sys.argv)
    
    # Obtener configuración de conexión desde la UI, si está disponible.
    config = get_connection_config()
    if not config:
        # Si no se obtuvo la configuración, usamos la configuración por defecto.
        config = CONNECTION_CONFIG
    
    # Configurar la instancia y obtener el engine de conexión a la base de datos.
    set_default_instance(config)
    engine = get_db_connection()
    if engine is None:
        sys.exit(0)
    
    # Intentamos obtener la instancia actual real; si no se logra, usamos la función simulada.
    instance_actual = get_current_instance(engine)
    if not instance_actual:
        instance_actual = conectar_instancia()
    
    # Crear y mostrar la ventana de importación.
    import_window = ImportWindow(instance_actual, config)
    import_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
