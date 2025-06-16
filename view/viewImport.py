# view/viewImport.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableView, QFrame, QLineEdit
)
from PyQt5.QtCore import pyqtSlot
from model.pandas_model import PandasModel          # Importa el modelo virtual
from connect.importacion import importar_datos        # Función que obtiene el DataFrame
from style.importacion import style_sheet

class ImportWindow(QMainWindow):
    """
    Ventana para la importación de datos con un diseño moderno.
    Muestra la instancia conectada, parámetros de entrada y un botón para importar datos,
    así como un QTableView para visualizar los datos resultantes.
    """
    def __init__(self, instance_name, connection_config):
        """
        instance_name: Cadena que indica el nombre/identificador de la instancia.
        connection_config: Diccionario con la configuración de conexión.
        """
        super().__init__()
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(style_sheet)
        
        self.connection_config = connection_config  # Guardamos la configuración para la consulta

        # Widget central y layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Panel de Control
        self.control_frame = QFrame()
        self.control_frame.setObjectName("controlFrame")
        control_layout = QHBoxLayout(self.control_frame)
        
        # Etiqueta que muestra la instancia
        self.instance_label = QLabel(f"Instancia: {instance_name}")
        control_layout.addWidget(self.instance_label)
        
        # Botón para importar datos
        self.import_button = QPushButton("Importar Datos")
        self.import_button.clicked.connect(self.on_importar_datos)
        control_layout.addWidget(self.import_button)
        
        self.main_layout.addWidget(self.control_frame)
        
        # Área de Datos: QTableView para mostrar la información
        self.table_view = QTableView()
        self.main_layout.addWidget(self.table_view)
    
    @pyqtSlot()
    def on_importar_datos(self):
        """
        Llama a la función importar_datos() de importacion.py (con try/except).
        Si se obtienen datos, crea una instancia de PandasModel y la asigna a la QTableView.
        En caso de error o si el DataFrame está vacío, muestra un mensaje.
        """
        self.import_button.setEnabled(False)
        try:
            df = importar_datos(self.connection_config)
        except Exception as e:
            df = None
            self.mostrar_error(f"Error durante la importación: {e}")
        finally:
            self.import_button.setEnabled(True)
        
        if df is None or df.empty:
            self.mostrar_error("No se encontraron datos.")
        else:
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()
    
    def mostrar_error(self, mensaje):
        """
        Muestra en la vista un mensaje de error utilizando un modelo simple.
        """
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        error_model = QStandardItemModel()
        error_model.setHorizontalHeaderLabels(["Error"])
        error_model.appendRow([QStandardItem(mensaje)])
        self.table_view.setModel(error_model)
