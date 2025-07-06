import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV Cleaner", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def card(header, value, sub, **styles):
    st.markdown(f'''
    <div class="card" style="{styles.get('extra','')}">
        <small>{header}</small>
        <h1 style="margin:0">{value}</h1>
        <h4 style="margin:0">{sub}</h4>
    </div>''', unsafe_allow_html=True)
st.title("Limpiador CSV → GoHighLevel")
 
file = st.file_uploader("Sube tu CSV de productos", type=["csv"])
if file:
     import requests
     import io

     try:
         # Enviar el archivo al backend de FastAPI
         files = {'file': (file.name, file.getvalue(), file.type)}
         response = requests.post("http://localhost:8000/clean_csv/", files=files)
         response.raise_for_status()  # Lanza una excepción para códigos de estado de error (4xx o 5xx)

         # Recibir el CSV limpio del backend
         cleaned_csv_data = response.content
         cleaned_df = pd.read_csv(io.BytesIO(cleaned_csv_data))

         st.success("¡CSV procesado por el backend y listo para GoHighLevel!")
         st.dataframe(cleaned_df.head())

         st.download_button(
             label="Descargar CSV para GoHighLevel",
             data=cleaned_csv_data,
             file_name="productos_ghl_limpio.csv",
             mime="text/csv"
         )

     except requests.exceptions.RequestException as e:
         st.error(f"Error de conexión con el backend: {e}. Asegúrate de que el backend de FastAPI esté corriendo en http://localhost:8000.")
     except Exception as e:
         st.error(f"Error al procesar el archivo en Streamlit: {e}") 
 
else:
     st.info("Por favor, sube un archivo CSV para comenzar.")