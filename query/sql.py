# query/sql.py

QUERY_IMPORTACION = """
WITH ReferenciasSinExistenciaTotal AS (
    -- Identifica referencias donde la suma de existencias en todas las tiendas es 0
    SELECT 
        tbDimInventario.Referencia, 
        tbDimInventario.CodigoMarca
    FROM 
        tbDimInventario
    LEFT JOIN 
        tbHecInventario ON tbDimInventario.dimID_Inventario = tbHecInventario.dimid_inventario
    GROUP BY 
        tbDimInventario.Referencia, 
        tbDimInventario.CodigoMarca
    HAVING 
        SUM(tbHecInventario.Existencia) = 0
)
SELECT 
    tbDimInventario.Referencia,
    tbDimInventario.NombreMarca,
    tbDimInventario.CodigoMarca,
    tbDimInventario.Nombre,
    tbDimInventario.Fabricante,
    tbDimCategorias.NombreSubLinea,
    tbDimInventario.NombreCategoria,
    CASE 
        WHEN tbDimTiendas.dimID_Tienda IN (2003) THEN 'Valencia Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (2005) THEN 'Oriente - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (
             1, 1002, 1004, 1006, 1009, 1010, 1011, 1012, 
             1013, 1014, 1017, 1018, 1019, 1020, 1021, 1022, 
             1023, 1024
        ) THEN 'Oriente - Sucursales'
        WHEN tbDimTiendas.dimID_Tienda IN (2004) THEN 'Occidente - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (
             1026, 1027, 1028, 1029, 1030, 1031, 1037, 1038, 1039, 1040, 
             1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1050, 1052, 
             1053, 1055, 2007
        ) THEN 'Occidente - Sucursales'
        WHEN tbDimTiendas.dimID_Tienda IN (2006) THEN 'Margarita - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (1032, 1033, 1034, 1035, 1036) THEN 'Margarita - Sucursales'
        ELSE 'Sin region'
    END AS Region,
    SUM(tbHecInventario.Existencia) AS Existencia_Total
FROM 
    tbDimInventario
LEFT JOIN 
    tbHecInventario ON tbDimInventario.dimID_Inventario = tbHecInventario.dimid_inventario
LEFT JOIN 
    tbDimTiendas ON tbHecInventario.dimid_tienda = tbDimTiendas.dimID_Tienda
LEFT JOIN
    tbDimCategorias ON tbDimInventario.dimID_Categoria = tbDimCategorias.dimID_Categoria
WHERE 
    NOT EXISTS (
        SELECT 1 
        FROM ReferenciasSinExistenciaTotal R
        WHERE R.Referencia = tbDimInventario.Referencia 
          AND R.CodigoMarca = tbDimInventario.CodigoMarca
    )
GROUP BY 
    tbDimInventario.Referencia,
    tbDimInventario.NombreMarca,
    tbDimInventario.CodigoMarca,
    tbDimInventario.Nombre,
    tbDimInventario.Fabricante,
    tbDimCategorias.NombreSubLinea,
    tbDimInventario.NombreCategoria,
    tbDimTiendas.dimID_Tienda,
    CASE 
        WHEN tbDimTiendas.dimID_Tienda IN (2003) THEN 'Valencia Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (2005) THEN 'Oriente - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (
             1, 1002, 1004, 1006, 1009, 1010, 1011, 1012, 
             1013, 1014, 1017, 1018, 1019, 1020, 1021, 1022, 
             1023, 1024
        ) THEN 'Oriente - Sucursales'
        WHEN tbDimTiendas.dimID_Tienda IN (2004) THEN 'Occidente - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (
             1026, 1027, 1028, 1029, 1030, 1031, 1037, 1038, 1039, 1040, 
             1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1050, 1052, 
             1053, 1055, 2007
        ) THEN 'Occidente - Sucursales'
        WHEN tbDimTiendas.dimID_Tienda IN (2006) THEN 'Margarita - Casa Matriz'
        WHEN tbDimTiendas.dimID_Tienda IN (1032, 1033, 1034, 1035, 1036) THEN 'Margarita - Sucursales'
        ELSE 'Sin region'
    END
HAVING 
    (tbDimTiendas.dimID_Tienda <> 2003 OR SUM(tbHecInventario.Existencia) > 0)
ORDER BY 
    tbDimInventario.Referencia;
"""

def obtener_consulta_importacion(offset=0, limit=10000):
    # Usa directamente la consulta por defecto
    consulta_base = QUERY_IMPORTACION.strip().rstrip(';')
    consulta = f"{consulta_base} LIMIT {limit} OFFSET {offset};"
    return consulta

if __name__ == "__main__":
    consulta = obtener_consulta_importacion(offset=0, limit=10000)
    print("Consulta generada:")
    print(consulta)
