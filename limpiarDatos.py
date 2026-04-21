import csv
import os
import re
from glob import glob
from openpyxl import Workbook
import pandas as pd


def cargarDatosCsv():
    carpeta = "Data"

    archivos = glob(os.path.join(carpeta, "*.csv"))

    datos_finales = {}
    horas_totales = set()

    meses = { "Ene": 1,"Feb": 2,"Mar": 3,"Abr": 4,"May": 5, "Jun": 6, "Jul": 7,"Ago": 8,"Sep": 9,"Oct": 10, "Nov": 11,"Dic": 12}

    for archivo in archivos:

        with open(archivo, encoding="utf-8") as f:
            reader = csv.reader(f)
            filas = list(reader)

            encabezado = filas[0]
            valores = filas[1]

            for i in range(4, len(encabezado)):  # desde columna tiempo
                texto_fecha = encabezado[i]
                
                # Thu Feb 05 2026 14:59:40 GMT-0500 (hora estándar de Colombia)
                # Buscar fecha y hora
                m = re.search(r'(\w{3}) (\w{3}) (\d{2}) (\d{4}) (\d{2}:\d{2}:\d{2})', texto_fecha)
                if m:
                    dia = m.group(3)
                    anio = m.group(4)
                    mes = meses[m.group(2)]
                    hora = m.group(5)

                    fecha = f"{mes}/{dia}/{anio}"

                    valor = valores[i]

                    if fecha not in datos_finales:
                        datos_finales[fecha] = {}

                    datos_finales[fecha][hora] = int(valor)
                    horas_totales.add(hora)

    # Ordenar horas
    horas_ordenadas = sorted(horas_totales)

    # Crear Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Consolidado"

    # Encabezado
    ws.append(["Fecha"] + horas_ordenadas)
    data = []
    # Datos
    for fecha in sorted(datos_finales.keys()):
        fila = [fecha]
        filaDataFrame = {"Fecha": fecha}

        for hora in horas_ordenadas:
            fila.append(datos_finales[fecha].get(hora, ""))
            filaDataFrame[hora] = datos_finales[fecha].get(hora, None)
        
        data.append(filaDataFrame)

        ws.append(fila)
    df = pd.DataFrame(data)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")


    # Guardar
    salida = os.path.join(carpeta, "Consolidado.xlsx")
    wb.save(salida)
    return(df)

