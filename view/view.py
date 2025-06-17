from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableView, QFrame, QProgressBar
)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import time
from connect.importacion import importar_datos_generator
from style.importacionStyle import get_style_sheet_importacion
from model.pandas_model import PandasModel

class ImportWindow(QMainWindow):
    """Ventana con scroll infinito para importar datos dinámicamente."""
    def __init__(self, instance_name, connection_config):
        super().__init__()
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(get_style_sheet_importacion)
        self.connection_config = connection_config

        # Paginación y acumulación de bloques de datos
        self.offset = 0  
        self.limit = 10000  
        self.data_blocks = []  # Lista para almacenar cada bloque de datos
        self.pandas_model = PandasModel()  

        # Widget central y layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Panel de Control
        self.control_frame = QFrame()
        self.control_frame.setObjectName("controlFrame")
        control_layout = QHBoxLayout(self.control_frame)

        # Etiqueta de instancia conectada
        self.instance_label = QLabel(f"Instancia: {instance_name}")
        control_layout.addWidget(self.instance_label)

        # Barra de progreso para la carga de datos
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)

        # Botón para iniciar la importación
        self.import_button = QPushButton("Importar Datos")
        self.import_button.clicked.connect(self.on_importar_datos)
        control_layout.addWidget(self.import_button)

        self.main_layout.addWidget(self.control_frame)

        # QTableView con scroll infinito; se mantiene la conexión al scroll
        self.table_view = QTableView()
        self.table_view.setModel(self.pandas_model)
        self.table_view.verticalScrollBar().valueChanged.connect(self.detectar_scroll)
        self.main_layout.addWidget(self.table_view)

    @pyqtSlot()
    def on_importar_datos(self):
        """Carga los datos iniciales y acumula el primer bloque."""
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        try:
            inicio = time.time()
            df = importar_datos_generator(self.connection_config, total_rows=50000, batch_size=self.limit)
            fin = time.time()
            tiempo = fin - inicio

            if df is None or df.empty:
                self.mostrar_error("No se encontraron datos.")
                return

            # Reiniciamos la paginación y acumulación
            self.offset = self.limit  
            self.data_blocks = [df]
            # Actualizamos el modelo con el bloque inicial
            self.pandas_model.actualizar_datos(df)
            self.table_view.resizeColumnsToContents()
            print(f"✅ Bloque importado: OFFSET 0 - {self.limit} filas ({tiempo:.2f} segundos)")

        except Exception as e:
            self.mostrar_error(f"Error durante la importación: {e}")

        finally:
            self.import_button.setEnabled(True)
            self.progress_bar.setVisible(False)

    def detectar_scroll(self, value):
        """Detecta si se alcanzó el final del scroll para disparar la carga de más datos."""
        if value == self.table_view.verticalScrollBar().maximum():
            self.on_cargar_mas_datos()

    @pyqtSlot()
    def on_cargar_mas_datos(self):
        """Carga más datos, acumula el bloque y actualiza el modelo sin reiniciarlo."""
        self.progress_bar.setVisible(True)
        try:
            inicio = time.time()
            df_more = importar_datos_generator(self.connection_config, total_rows=50000, batch_size=self.limit)
            fin = time.time()
            tiempo = fin - inicio

            if df_more is None or df_more.empty:
                print("⚠️ No se encontraron datos en el siguiente bloque.")
                return

            # Acumulamos el nuevo bloque (opción: evitar concatenar cada vez, pero si deseas el total actualizado)
            self.data_blocks.append(df_more)
            self.df_data = pd.concat(self.data_blocks, ignore_index=True)
            # Se actualiza el modelo con el nuevo bloque; se asume que 'actualizar_datos' agrega datos y emite señales de cambio
            self.pandas_model.actualizar_datos(df_more)
            self.table_view.resizeColumnsToContents()
            print(f"✅ Bloque importado: OFFSET {self.offset} - {self.limit} filas ({tiempo:.2f} segundos)")
            self.offset += self.limit

        except Exception as e:
            self.mostrar_error(f"Error al cargar más datos: {e}")

        finally:
            self.progress_bar.setVisible(False)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en la vista mediante un modelo simple."""
        error_model = QStandardItemModel()
        error_model.setHorizontalHeaderLabels(["Error"])
        error_model.appendRow([QStandardItem(mensaje)])
        self.table_view.setModel(error_model)
        print(mensaje)
