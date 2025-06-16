# sql.py
QUERY_IMPORTACION = """
SELECT 
    DI.Referencia,
    DI.CodigoMarca,
    DI.NombreMarca,
    DC.NombreLinea,
    DI.NombreCategoria,
    ISNULL(
        FORMAT(
            ROUND(
                ((HI.PrecioDetalConIva - HI.PrecioPromocion) * 100.0) / NULLIF(HI.PrecioDetalConIva, 0),
                2
            ),
            'N2'
        ) + '%',
        '0%'
    ) AS Descuento,
    HI.Existencia,
    DT.Nombre AS NombreTienda
FROM tbHecInventario AS HI
INNER JOIN tbDimInventario AS DI
    ON HI.dimid_inventario = DI.dimID_Inventario
INNER JOIN tbDimCategorias AS DC
    ON DI.dimID_Categoria = DC.dimID_Categoria
INNER JOIN tbDimTiendas AS DT
    ON DT.dimID_Tienda = HI.dimID_Tienda
INNER JOIN (
    SELECT 
        CodigoBarra,
        Referencia,
        Existencia
    FROM [J101010100_999999].dbo.INVENTARIO
    WHERE Existencia >= 0
) V
    ON DI.CodigoBarra = V.CodigoBarra;
"""

def obtener_consulta_importacion():
    """
    Retorna la consulta SQL para uso en la importación.
    """
    return QUERY_IMPORTACION

if __name__ == "__main__":
    print(obtener_consulta_importacion())
