import pandas as pd
import glob
import os


archivos_csv = glob.glob("datos/sucursal_*.csv")
archivos_xlsx = glob.glob("datos/sucursal_*.xlsx")

lista_informes = []

for archivo in archivos_csv:
    try:
        df = pd.read_csv(archivo, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(archivo, encoding="latin-1")

    lista_informes.append(df)
    print(f"Leído: {archivo} - {len(df)} filas")

for archivo in archivos_xlsx:
    df = pd.read_excel(archivo, engine="openpyxl")
    lista_informes.append(df)
    print(f"Leído: {archivo} - {len(df)} filas")


for i, df in enumerate(lista_informes):

    # Bogotá tiene nombres diferentes
    if "Fecha_Venta" in df.columns:

        lista_informes[i] = df.rename(columns={
            "Fecha_Venta": "fecha",
            "Producto": "producto",
            "Categoria": "categoria",
            "Cant": "cantidad",
            "Valor_Unitario": "precio_unitario",
            "Vendedor": "vendedor",
            "Pago": "metodo_pago"
        })


df_consolidado = pd.concat(lista_informes, ignore_index=True)

print("\nColumnas después del renombrado:")
print(df_consolidado.columns.tolist())


filas_antes = len(df_consolidado)

duplicados = df_consolidado.duplicated().sum()

df_consolidado = df_consolidado.drop_duplicates().reset_index(drop=True)

filas_despues = len(df_consolidado)

print("\nLimpieza de duplicados:")
print(f"Filas antes: {filas_antes}")
print(f"Duplicados encontrados: {duplicados}")
print(f"Filas después: {filas_despues}")


print("\nDatos vacíos antes de limpiar:")
print(df_consolidado.isnull().sum())


df_consolidado["vendedor"] = df_consolidado["vendedor"].fillna(
    "No especificado"
)

df_consolidado["metodo_pago"] = df_consolidado["metodo_pago"].fillna(
    "No especificado"
)

df_consolidado["precio_unitario"] = pd.to_numeric(
    df_consolidado["precio_unitario"],
    errors="coerce"
)

mediana_general = df_consolidado["precio_unitario"].median()

df_consolidado["precio_unitario"] = (
    df_consolidado.groupby("producto")["precio_unitario"]
    .transform(lambda x: x.fillna(x.median()))
)

df_consolidado["precio_unitario"] = df_consolidado[
    "precio_unitario"
].fillna(mediana_general)



print("\nDatos vacíos después de limpiar:")
print(df_consolidado.isnull().sum())



os.makedirs("salida", exist_ok=True)

ruta_salida = "salida/consolidado_limpio.xlsx"

df_consolidado.to_excel(ruta_salida, index=False)

print("\n============================================")
print("¡PROCESO TERMINADO!")
print("============================================")
print(f"Archivo guardado en: {ruta_salida}")
print(f"Total de filas limpias: {len(df_consolidado)}")
print(f"Total de columnas: {len(df_consolidado.columns)}")