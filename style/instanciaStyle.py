def get_instancia_stylesheet():
    return """
        QDialog {
            background-color: #18191a;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            color: #e4e6eb;
            padding: 20px;
            border-radius: 10px;
        }
        QLabel {
            color: #ced0ce;
            margin-bottom: 6px;
            font-weight: 500;
        }
        QLineEdit, QComboBox, QCheckBox {
            background-color: #242526;
            border: 1px solid #3a3b3c;
            padding: 10px;
            border-radius: 8px;
            color: #e4e6eb;
            margin-bottom: 15px;
        }
        /* Mejora en el drop-down del ComboBox */
        QComboBox::drop-down {
            subcontrol-origin: content;
            subcontrol-position: top right;
            width: 30px;
            border-left: 1px solid #3a3b3c;
            margin-left: 5px;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #242526;
            border: 1px solid #3a3b3c;
            border-radius: 8px;
            color: #e4e6eb;
            selection-background-color: #0084ff;
            padding: 5px;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 10px;
        }
        QComboBox QAbstractItemView::item:last-child {
            border: none;
        }
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #0084ff, stop:1 #005cbf);
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 30px;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #339eff, stop:1 #0073e6);
        }
        QPushButton:pressed {
            background-color: #003d80;
        }
        QFormLayout QLabel {
            min-width: 120px;
        }
    """
