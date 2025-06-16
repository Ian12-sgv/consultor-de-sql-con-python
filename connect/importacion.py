# importacion.py

import pandas as pd
from query.consulta import obtener_datos

def conectar_instancia():
    """
    Conecta a la instancia real o simula la conexión.
    Retorna el nombre de la instancia a la que se ha conectado.
    """
    # Aquí podrías implementar la lógica real de conexión.
    # Para simplificar, en este ejemplo se simula devolviendo un nombre.
    instance_name = "MiInstancia"
    print(f"Conectado a la instancia: {instance_name}")
    return instance_name

def importar_datos(config):
    """
    Ejecuta la importación de datos utilizando la consulta SQL definida en sql.py, a través de
    la función obtener_datos().
    
    Parámetros:
      config (dict): Diccionario con la configuración de conexión, que debe contener:
          - 'login': usuario,
          - 'password': contraseña,
          - 'server_name': nombre del servidor/instancia (formato 'SERVIDOR\\INSTANCIA'),
          - 'database': (opcional) la base de datos a usar (por defecto 'BODEGA_DATOS').
    
    Retorna:
      DataFrame con los datos importados. Si la consulta falla o no se obtienen datos, retorna un
      DataFrame vacío.
    """
    try:
        # Se ejecuta la obtención de datos a partir de la configuración
        df = obtener_datos(config)
        
        if not df.empty:
            print("Datos importados correctamente.")
        else:
            print("No se pudieron importar datos.")
            
        return df
    except Exception as e:
        print("Error durante la importación de datos:", e)
        return pd.DataFrame()

if __name__ == "__main__":
    # Ejemplo de uso para pruebas locales
    config = {
        'login': 'sa',
        'password': 'tu_contraseña',
        'server_name': 'MyServer\\MyInstance',
        'database': 'BODEGA_DATOS'
    }
    # Primero, conectamos (simulado)
    instancia = conectar_instancia()
    # Luego, intentamos importar los datos
    df_importado = importar_datos(config)
    print("Datos obtenidos:")
    print(df_importado.head())
