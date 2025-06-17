# pandas_model.py
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._data = df

    def actualizar_datos(self, df):
        self.beginResetModel()
        self._data = df.copy()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                try:
                    return self._data.columns[section]
                except IndexError:
                    return ""
            else:
                return section
        return None
