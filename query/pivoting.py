# pivoting.py
import pandas as pd

def transformar_datos(df):
    """
    Transforma el DataFrame realizando un pivot.

    Se asume que el DataFrame contiene, al menos, las siguientes columnas:
      - Referencia: identificador o nombre del producto.
      - NombreTienda: nombre de la tienda (se convertirá en columnas).
      - Existencia: valor correspondiente que se asignará a cada celda pivotada.
    
    Retorna un DataFrame transformado donde cada tienda es una columna.
    """
    try:
        # Realiza el pivot: cada 'NombreTienda' se convierte en columna,
        # y se asigna el valor de 'Existencia' correspondiente para cada 'Referencia'
        pivot_df = df.pivot(index='Referencia', columns='NombreTienda', values='Existencia')
        # Reinicia el índice para que 'Referencia' pase a ser una columna normal
        pivot_df = pivot_df.reset_index()
    except Exception as e:
        print("Error al transformar los datos:", e)
        # En caso de error, retorna el DataFrame original
        pivot_df = df
    return pivot_df

if __name__ == "__main__":
    # Ejemplo de uso:
    data = {
        'Referencia': ['A', 'B', 'A', 'B'],
        'NombreTienda': ['Tienda1', 'Tienda1', 'Tienda2', 'Tienda2'],
        'Existencia': [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)
    print("DataFrame original:")
    print(df, "\n")
    
    df_transformado = transformar_datos(df)
    print("DataFrame transformado (pivot):")
    print(df_transformado)
