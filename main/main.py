import sys
import os

# Ajustamos el path para incluir el directorio padre
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

# Ahora importamos desde los paquetes correspondientes
from view.instanciaUI import get_connection_config
from connect.instancia import get_current_instance
from connect.db import set_default_instance, get_db_connection
from PyQt5.QtWidgets import QApplication

# Importamos la ventana de importación definida en viewImport.py
from view.viewImport import ImportWindow

def main():
    app = QApplication(sys.argv)
    
    # Obtenemos la configuración de conexión.
    config = get_connection_config()
    if not config:
        print("No se obtuvo configuración de conexión. Finalizando aplicación.")
        sys.exit(0)
    
    # Configuramos la instancia de conexión y obtenemos el engine
    set_default_instance(config)
    engine = get_db_connection()
    if engine is None:
        print("No se pudo establecer la conexión a la base de datos.")
        sys.exit(0)
    
    # Obtenemos el nombre (o identificador) de la instancia actual
    instance_actual = get_current_instance(engine)
    print("Conectado a la instancia:", instance_actual)
    
    # Redirigimos a la ventana de importación, pasando tanto el nombre de la instancia
    # como la configuración de conexión.
    import_window = ImportWindow(instance_actual, config)
    import_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
