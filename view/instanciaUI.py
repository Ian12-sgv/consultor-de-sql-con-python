# instancia_ui.py
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import logging
# Importamos la lógica desde el módulo dedicado.
from connect.instancia import get_available_sql_servers, get_default_username, load_connection_config, save_connection_config
# Importa la función de estilos desde la carpeta style.
from style.instanciaStyle import get_instancia_stylesheet

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

class ConnectionConfigDialog(QDialog):
    """
    Diálogo modal para configurar la conexión utilizando PyQt5 con un estilo moderno.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None

        # Precargar la configuración guardada (si existe) usando la lógica.
        self.saved_config = load_connection_config()

        self.setWindowTitle("Configuración de Conexión")
        self.setFixedSize(500, 600)
        self._apply_styles()

        # Layout principal del diálogo.
        layout = QVBoxLayout(self)

        # Formulario de configuración.
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # Server Type (fijo)
        self.server_type_edit = QLineEdit("Database Engine")
        self.server_type_edit.setReadOnly(True)
        form_layout.addRow("Server Type:", self.server_type_edit)

        # Server Name (ComboBox)
        self.server_name_combo = QComboBox()
        self.available_instances = get_available_sql_servers()
        if self.available_instances:
            self.server_name_combo.addItems(self.available_instances)
            # Si tenemos configuración guardada, seleccionamos la instancia guardada, si existe.
            if self.saved_config and "server_name" in self.saved_config:
                idx = self.server_name_combo.findText(self.saved_config["server_name"])
                if idx >= 0:
                    self.server_name_combo.setCurrentIndex(idx)
        else:
            self.server_name_combo.addItem("Ingrese el servidor...")
        form_layout.addRow("Server Name:", self.server_name_combo)

        # Botón para actualizar instancias.
        self.refresh_button = QPushButton("Actualizar instancias")
        self.refresh_button.clicked.connect(self.refresh_instances)
        form_layout.addRow("", self.refresh_button)

        # Authentication.
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["Windows Authentication", "SQL Server Authentication"])
        self.auth_combo.currentTextChanged.connect(self.update_auth_fields)
        form_layout.addRow("Authentication:", self.auth_combo)

        # Login.
        self.login_edit = QLineEdit(get_default_username())
        if self.saved_config and "login" in self.saved_config:
            self.login_edit.setText(self.saved_config["login"])
        form_layout.addRow("Login:", self.login_edit)

        # Password.
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        if self.saved_config and "password" in self.saved_config:
            self.password_edit.setText(self.saved_config["password"])
        form_layout.addRow("Password:", self.password_edit)

        # Checkbox para mostrar/ocultar contraseña.
        self.show_password_chk = QCheckBox("Mostrar contraseña")
        self.show_password_chk.stateChanged.connect(self.toggle_password)
        form_layout.addRow("", self.show_password_chk)

        # Checkbox para recordar password.
        self.remember_chk = QCheckBox("Recordar password")
        if self.saved_config:
            self.remember_chk.setChecked(True)
        form_layout.addRow("", self.remember_chk)

        # Botones: Guardar y Conectar.
        button_layout = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar")
        self.guardar_btn.clicked.connect(self.on_submit)
        self.conectar_btn = QPushButton("Conectar")
        self.conectar_btn.clicked.connect(self.on_connect)
        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.conectar_btn)
        layout.addLayout(button_layout)

    def _apply_styles(self):
        """Aplica un stylesheet moderno y oscuro a la ventana y sus widgets."""
        self.setStyleSheet(get_instancia_stylesheet())

    def toggle_password(self, state):
        """Muestra u oculta la contraseña según el estado del checkbox."""
        if state == Qt.Checked:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)

    def refresh_instances(self):
        """Actualiza la lista de instancias de SQL Server."""
        self.available_instances = get_available_sql_servers()
        self.server_name_combo.clear()
        self.server_name_combo.addItems(self.available_instances)
        if self.available_instances:
            self.server_name_combo.setCurrentIndex(0)
        logging.debug("Instancias actualizadas: %s", self.available_instances)

    def update_auth_fields(self):
        """
        Habilita o deshabilita los campos Login y Password según la autenticación seleccionada.
        """
        if self.auth_combo.currentText() == "Windows Authentication":
            self.login_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.login_edit.setText(get_default_username())
            self.password_edit.setText("")
        else:
            self.login_edit.setEnabled(True)
            self.password_edit.setEnabled(True)

    def on_submit(self):
        """Recoge la configuración sin probar la conexión y cierra el diálogo."""
        self.result = self.get_config()
        # Utiliza la lógica para guardar la configuración.
        if self.result.get("remember"):
            save_connection_config(self.result)
        self.accept()

    def on_connect(self):
        """
        Recoge la configuración, establece la conexión y prueba la conexión.
        En este diálogo solo devolvemos los datos; la prueba de conexión se realiza en el flujo principal.
        """
        self.result = self.get_config()
        if self.result.get("remember"):
            save_connection_config(self.result)
        self.accept()

    def get_config(self):
        """Retorna la configuración recogida en forma de diccionario."""
        return {
            "server_type": self.server_type_edit.text(),
            "server_name": self.server_name_combo.currentText(),
            "auth": self.auth_combo.currentText(),
            "login": self.login_edit.text(),
            "password": self.password_edit.text(),
            "remember": self.remember_chk.isChecked()
        }

def get_connection_config(parent=None):
    """
    Muestra el diálogo de configuración y retorna la configuración ingresada.
    Retorna None si se cancela.
    """
    dialog = ConnectionConfigDialog(parent)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        return dialog.result
    else:
        return None

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    config = get_connection_config()
    if config:
        print("Configuración obtenida:")
        print(config)
    else:
        print("No se obtuvo configuración.")
