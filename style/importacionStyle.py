# style/importacion.py

def get_style_sheet_importacion():
    """
    Retorna el style sheet de la aplicación.
    """
    return """
    /* General */
    QMainWindow, QWidget {
        background-color: #F8F9FA;
        font-family: "Segoe UI", sans-serif;
    }

    /* Header */
    #headerFrame {
        background-color: #2C3E50;
        padding: 20px;
        border-bottom: 1px solid #34495E;
    }
    #headerFrame QLabel {
        color: #ECF0F1;
        font-size: 26px;
        font-weight: bold;
    }

    /* Panel de Control */
    #controlFrame {
        background-color: #FFFFFF;
        border: 1px solid #CED4DA;
        border-radius: 8px;
        padding: 15px;
        margin: 20px;
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #CED4DA;
        border-radius: 4px;
        font-size: 15px;
        margin-right: 10px;
    }
    QPushButton {
        background-color: #007BFF;
        color: #FFFFFF;
        font-size: 15px;
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }

    /* Área de Datos - QTreeView */
    QTreeView {
        background-color: #FFFFFF;
        border: 1px solid #CED4DA;
        font-size: 14px;
        margin: 20px;
        padding: 10px;
    }
    """
