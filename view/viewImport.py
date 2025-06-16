# viewImport.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTreeView, QFrame, QLineEdit
)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem
# Se importa la función obtener_datos de consulta.py:
from query.consulta import obtener_datos  # Asegúrate de que la ruta sea correcta según tu estructura.
from style.importacion import style_sheet

class ImportWindow(QMainWindow):
    """
    Ventana para la importación de datos con un diseño moderno.
    Muestra la instancia conectada, parámetros de entrada y un botón para importar datos,
    así como un QTreeView para visualizar los datos resultantes.
    """
    def __init__(self, instance_name, connection_config):
        """
        connection_config: Diccionario con la configuración de conexión que se usará para la consulta.
        """
        super().__init__()
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(style_sheet)
        
        self.connection_config = connection_config  # Guardamos la configuración para usarla en la consulta

        # Widget central y layout principal (vertical)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Panel de Control
        self.control_frame = QFrame()
        self.control_frame.setObjectName("controlFrame")
        control_layout = QHBoxLayout(self.control_frame)
        
        # Etiqueta para mostrar la instancia (opcional)
        self.instance_label = QLabel(f"Instancia: {instance_name}")
        control_layout.addWidget(self.instance_label)
        
        # Botón para importar datos
        self.import_button = QPushButton("Importar Datos")
        self.import_button.clicked.connect(self.importar_datos)
        control_layout.addWidget(self.import_button)
        
        self.main_layout.addWidget(self.control_frame)
        
        # Área de Datos: QTreeView para mostrar información
        self.tree_view = QTreeView()
        self.init_tree_view()
        self.main_layout.addWidget(self.tree_view)
    
    def init_tree_view(self):
        """
        Inicializa el modelo para la QTreeView con encabezados.
        Se configuran tres columnas, pero puedes ajustar según la cantidad de columnas
        que retorne tu consulta.
        """
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['Columna 1', 'Columna 2', 'Columna 3'])
        self.tree_view.setModel(self.tree_model)
        self.tree_view.header().setStretchLastSection(True)
    
    @pyqtSlot()
    def importar_datos(self):
        """
        Llama a la función obtener_datos() de consulta.py, pasando la configuración,
        para obtener el DataFrame con la información consultada y actualiza el QTreeView.
        """
        # Se pasa la configuración a la función obtener_datos.
        df = obtener_datos(self.connection_config)
        
        # Limpiar los datos anteriores en el QTreeView.
        self.tree_model.removeRows(0, self.tree_model.rowCount())
        
        if df.empty:
            # Si el DataFrame está vacío, se muestra un mensaje en una fila.
            item = QStandardItem("No se encontraron datos.")
            self.tree_model.appendRow([item])
            return
        
        # Agregar las filas del DataFrame al modelo.
        # Se asume que el DataFrame tiene al menos tres columnas; ajusta si es necesario.
        for idx, row in df.iterrows():
            # Convertir cada valor a cadena para que se muestre en los QStandardItem.
            items = [QStandardItem(str(row[col])) for col in df.columns[:3]]
            self.tree_model.appendRow(items)
