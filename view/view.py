# ui/interfaz.py (o view.py)
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

# Solo importamos la transformación, ya que la conexión se realiza externamente.
from query.pivoting import transformar_datos

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(PandasModel, self).__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            elif orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None

def crear_interfaz(engine):
    """
    Crea la interfaz de usuario a partir del engine ya configurado.
    Se asume que el engine se ha creado previamente y que se puede usar para ejecutar la consulta.
    """
    # Definir la consulta de prueba; aquí se asume que la tabla existe en tu base de datos.
    query = "SELECT TOP 10 * FROM alguna_tabla"  # Reemplaza 'alguna_tabla' por una tabla real

    try:
        # Ejecutamos la consulta usando el engine proporcionado.
        df_origen = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return

    # Transformamos los datos (por ejemplo, pivot).
    df_transformado = transformar_datos(df_origen)

    # Creamos la aplicación PyQt y construimos la interfaz.
    app = QApplication(sys.argv)
    ventana = QWidget()
    ventana.setWindowTitle("Inventario de Tiendas")
    layout = QVBoxLayout()

    modelo = PandasModel(df_transformado)
    tabla = QTableView()
    tabla.setModel(modelo)
    tabla.resizeColumnsToContents()

    layout.addWidget(tabla)
    ventana.setLayout(layout)
    ventana.resize(800, 600)
    ventana.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    # Para pruebas locales se puede configurar la conexión aquí, pero en producción la
    # conexión vendrá del flujo principal (por ejemplo, main.py).
    
    # Ejemplo temporal (solo para probar):
    from connect.db import set_default_instance, get_db_connection
    config = {
        'login': 'tu_usuario',
        'password': 'tu_contraseña',
        'server_name': 'nombre_del_servidor'
    }
    set_default_instance(config)
    engine = get_db_connection()
    if engine:
        crear_interfaz(engine)
    else:
        print("No se pudo establecer la conexión a la base de datos.")
