from collections import defaultdict
import os

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Cargar datos
df = pd.read_excel("Data/Consolidado.xlsx")
st.sidebar.image("Imagenes\image.png", use_container_width=True)
grupos = defaultdict(list)
time_cols = df.columns.drop("Fecha")

for col in time_cols:
    partes = col.split(":")   # hh:mm:ss
    
    clave = partes[0]                 # 00

    # segundo exacto

    grupos[clave].append(col)
resultado = df.copy()

for grupo, columnas in grupos.items():
    resultado[grupo] = df[columnas].mean(axis=1)

columnas_base = [c for c in df.columns if ":" not in c]

df = resultado[columnas_base + list(grupos.keys())]




# Chat
pregunta = st.chat_input("Haz una pregunta sobre los datos")

if pregunta:

    contexto = df.head(50).to_string()

    prompt = f"""
    Eres un analista de datos.
    Responde preguntas usando esta tabla:

    {contexto}

    Esta tabala respesante la disponibilidad de restaurantes que tiene un dia y a una hora en especifico la aplicacion rapy, este es el promedio por hora.

    Pregunta:
    {pregunta}

    Reglas importantes:
     * Si la pregunta no es relacionada a los datos responde: "No estoy capacitado a responder eso, hacem una pregunta de los datos." 
     * Tus respuestas solo pueden estar vasadas en la informacion que esta en los datos no busques en internte. 
     * Responde a la pregunta con palabras. 
     * No muestres como hacerlo en un lenguaje de progamacion.
     * Redondea tu respuesta a dos sifras decimales.
    """

    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    st.chat_message("user").write(pregunta)
    st.chat_message("assistant").write(
        respuesta.choices[0].message.content
    )