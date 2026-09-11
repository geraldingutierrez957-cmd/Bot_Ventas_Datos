import pandas as pd
import os

ruta_datos = "datos"
ruta_salida = "salida"

os.makedirs(ruta_salida, exist_ok=True)


def leer_csv(ruta):
    """
    Intenta leer el CSV usando UTF-8.
    Si falla, intenta con latin-1.
    """
    try:
        return pd.read_csv(ruta, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(ruta, encoding="latin-1")

medellin = leer_csv(
    os.path.join(ruta_datos, "sucursal_medellin.csv")
)

cali = leer_csv(
    os.path.join(ruta_datos, "sucursal_cali.csv")
)

bogota = pd.read_excel(
    os.path.join(ruta_datos, "sucursal_bogota.xlsx")
)

barranquilla = pd.read_excel(
    os.path.join(ruta_datos, "sucursal_barranquilla.xlsx")
)

bogota = bogota.rename(columns={
    "Fecha_Venta": "fecha",
    "Producto": "producto",
    "Categoria": "categoria",
    "Cant": "cantidad",
    "Valor_Unitario": "precio_unitario",
    "Vendedor": "vendedor",
    "Pago": "metodo_pago"
})

medellin["sucursal"] = "Medellín"
cali["sucursal"] = "Cali"
bogota["sucursal"] = "Bogotá"
barranquilla["sucursal"] = "Barranquilla"

ventas = pd.concat(
    [medellin, cali, bogota, barranquilla],
    ignore_index=True
)

registros_originales = len(ventas)

ventas["fecha"] = pd.to_datetime(
    ventas["fecha"],
    errors="coerce",
    dayfirst=True
)

ventas["cantidad"] = pd.to_numeric(
    ventas["cantidad"],
    errors="coerce"
)

ventas["precio_unitario"] = pd.to_numeric(
    ventas["precio_unitario"],
    errors="coerce"
)


columnas_importantes = [
    "fecha",
    "producto",
    "categoria",
    "cantidad",
    "precio_unitario",
    "vendedor",
    "metodo_pago"
]

faltantes_antes = ventas[columnas_importantes].isna().sum()

columnas_texto = [
    "producto",
    "categoria",
    "vendedor",
    "metodo_pago",
    "sucursal"
]

for columna in columnas_texto:
    ventas[columna] = ventas[columna].fillna(
        "No especificado"
    )

    ventas[columna] = ventas[columna].astype(str).str.strip()

    ventas.loc[
        ventas[columna] == "",
        columna
    ] = "No especificado"

medianas_producto = (
    ventas[
        ventas["precio_unitario"].notna()
    ]
    .groupby("producto")["precio_unitario"]
    .median()
)

for indice in ventas.index:

    if pd.isna(ventas.loc[indice, "precio_unitario"]):

        producto = ventas.loc[indice, "producto"]

        if producto in medianas_producto.index:
            ventas.loc[indice, "precio_unitario"] = (
                medianas_producto[producto]
            )
mediana_general = ventas["precio_unitario"].median()

ventas["precio_unitario"] = ventas[
    "precio_unitario"
].fillna(mediana_general)
mediana_cantidad = ventas["cantidad"].median()

ventas["cantidad"] = ventas[
    "cantidad"
].fillna(mediana_cantidad)

duplicados = ventas.duplicated().sum()

ventas = ventas.drop_duplicates().reset_index(drop=True)

ventas["total_venta"] = (
    ventas["cantidad"] *
    ventas["precio_unitario"]
)

columnas_finales = [
    "fecha",
    "producto",
    "categoria",
    "cantidad",
    "precio_unitario",
    "vendedor",
    "metodo_pago",
    "sucursal",
    "total_venta"
]

ventas = ventas[columnas_finales]

ventas = ventas.sort_values(
    by="fecha",
    ascending=True
).reset_index(drop=True)

archivo_consolidado = os.path.join(
    ruta_salida,
    "ventas_consolidadas.csv"
)

ventas.to_csv(
    archivo_consolidado,
    index=False,
    encoding="utf-8-sig"
)

reporte = pd.DataFrame({
    "campo": faltantes_antes.index,
    "faltantes_detectados": faltantes_antes.values
})

reporte["registros_originales"] = registros_originales
reporte["duplicados_eliminados"] = duplicados
reporte["registros_finales"] = len(ventas)


archivo_reporte = os.path.join(
    ruta_salida,
    "reporte_calidad_datos.csv"
)

reporte.to_csv(
    archivo_reporte,
    index=False,
    encoding="utf-8-sig"
)

resumen = (
    ventas
    .groupby("sucursal")
    .agg(
        cantidad_registros=("sucursal", "size"),
        ventas_totales=("total_venta", "sum")
    )
    .reset_index()
)

archivo_resumen = os.path.join(
    ruta_salida,
    "resumen_por_sucursal.csv"
)

resumen.to_csv(
    archivo_resumen,
    index=False,
    encoding="utf-8-sig"
)

print()
print("==============================================")
print("           BOT DE VENTAS")
print("==============================================")
print()
print(f"Registros originales: {registros_originales}")
print(f"Duplicados eliminados: {duplicados}")
print(f"Registros finales: {len(ventas)}")
print()
print(
    f"Total de ventas: "
    f"${ventas['total_venta'].sum():,.0f}"
)
print()
print("Archivos generados correctamente:")
print()
print("- salida/ventas_consolidadas.csv")
print("- salida/reporte_calidad_datos.csv")
print("- salida/resumen_por_sucursal.csv")
print()
print("==============================================")