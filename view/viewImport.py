from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableView, QFrame, QProgressBar
)
from PyQt5.QtCore import pyqtSlot, Qt, QThread
import pandas as pd
import time
from style.importacionStyle import get_style_sheet_importacion  # Función que retorna un style sheet
from model.pandas_model import PandasModel  # Asegúrate de que PandasModel esté definido
from model.workers import ImportWorker  # Worker definido previamente

class ImportWindow(QMainWindow):
    """Ventana con scroll infinito para importar datos de manera incremental."""
    def __init__(self, instance_name, connection_config):
        super().__init__()
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet(get_style_sheet_importacion())
        self.connection_config = connection_config

        # Variables de paginación y almacenamiento
        self.offset = 0  
        self.limit = 10000  
        self.data_blocks = []  # Almacena cada bloque de datos
        self.pandas_model = PandasModel()  

        # Configuración del widget central y layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Panel de control
        self.control_frame = QFrame()
        self.control_frame.setObjectName("controlFrame")
        control_layout = QHBoxLayout(self.control_frame)

        # Etiqueta con el nombre de la instancia conectada
        self.instance_label = QLabel(f"Instancia: {instance_name}")
        control_layout.addWidget(self.instance_label)

        # Barra de progreso para la importación
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)

        # Botón para iniciar la importación de datos
        self.import_button = QPushButton("Importar Datos")
        self.import_button.clicked.connect(self.on_importar_datos)
        control_layout.addWidget(self.import_button)

        self.main_layout.addWidget(self.control_frame)

        # QTableView con scroll infinito
        self.table_view = QTableView()
        self.table_view.setModel(self.pandas_model)
        self.table_view.verticalScrollBar().valueChanged.connect(self.detectar_scroll)
        self.main_layout.addWidget(self.table_view)

    @pyqtSlot()
    def on_importar_datos(self):
        """Inicia la importación en un worker, movido a un hilo independiente."""
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        # Configuramos la barra de progreso basado en el número total de bloques
        total_blocks = 50000 // self.limit  # Ejemplo: 50000 filas / 10000 = 5 bloques
        self.progress_bar.setMaximum(total_blocks)
        self.progress_bar.setValue(0)
        self.offset = 0  # Reiniciamos el offset

        # Configuración del thread y el worker
        self.thread = QThread()
        self.worker = ImportWorker(self.connection_config, total_rows=50000, batch_size=self.limit)
        self.worker.moveToThread(self.thread)

        # Conectar señales y slots
        self.thread.started.connect(self.worker.run)
        self.worker.lote_recibido.connect(self.handle_lote_recibido)
        self.worker.error.connect(self.mostrar_error)
        self.worker.lote_recibido.connect(lambda offset, df: self.progress_bar.setValue(
            self.progress_bar.value() + 1))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.import_button.setEnabled(True))

        self.thread.start()

    @pyqtSlot(int, pd.DataFrame)
    def handle_lote_recibido(self, offset, df):
        """Actualiza el modelo agregando cada nuevo lote recibido."""
        if df is None or df.empty:
            self.mostrar_error("No se encontraron datos en el lote recibido.")
            return

        self.data_blocks.append(df)
        try:
            df_total = pd.concat(self.data_blocks, ignore_index=True)
        except Exception as e:
            self.mostrar_error(f"Error al concatenar datos: {e}")
            return

        self.pandas_model.actualizar_datos(df_total)
        self.table_view.resizeColumnsToContents()
        print(f"✅ Lote recibido: OFFSET {offset} - {self.limit} filas")
        self.offset = offset + self.limit

    def detectar_scroll(self, value):
        """Si se llega al final del scroll, dispara la carga de más datos."""
        if value == self.table_view.verticalScrollBar().maximum():
            self.on_cargar_mas_datos()

    @pyqtSlot()
    def on_cargar_mas_datos(self):
        """Carga adicional de datos (en este ejemplo se hace sin worker)."""
        self.progress_bar.setVisible(True)
        try:
            from connect.importacion import importar_datos_con_metricas
            inicio = time.time()
            df_more = importar_datos_con_metricas(self.connection_config, total_rows=50000, batch_size=self.limit)
            fin = time.time()
            if df_more is None or df_more.empty:
                print("⚠️ No se encontraron datos en el siguiente bloque.")
                return

            self.data_blocks.append(df_more)
            df_total = pd.concat(self.data_blocks, ignore_index=True)
            self.pandas_model.actualizar_datos(df_total)
            self.table_view.resizeColumnsToContents()
            print(f"✅ Bloque adicional importado: OFFSET {self.offset} - {self.limit} filas ({fin - inicio:.2f} seg)")
            self.offset += self.limit
        except Exception as e:
            self.mostrar_error(f"Error al cargar más datos: {e}")
        finally:
            self.progress_bar.setVisible(False)

    def mostrar_error(self, mensaje):
        """Muestra el mensaje de error (aquí se imprime en consola)."""
        print("Error:", mensaje)
