from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# Configurar CORS para permitir solicitudes desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Reemplaza con la URL de tu app Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/clean_csv/")
async def clean_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV.")

    try:
        # Leer el CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        if df.empty:
            raise HTTPException(status_code=400, detail="El archivo CSV está vacío.")

        # Lógica de limpieza y mapeo para GoHighLevel
        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('.', '', regex=False)
        df.columns = df.columns.str.replace('(', '', regex=False)
        df.columns = df.columns.str.replace(')', '', regex=False)
        df.columns = df.columns.str.replace('/', '_', regex=False)
        df.columns = df.columns.str.replace('-', '_', regex=False)
        df.columns = df.columns.str.lower()

        # Eliminar duplicados y filas completamente vacías
        df_clean = df.drop_duplicates().dropna(how="all")

        # Mapeo de columnas para GoHighLevel
        ghl_mapping = {
            'handle': 'Handle',
            'title': 'Title',
            'body_(html)': 'Body (HTML)',
            'included_in_online_store': 'Included in Online Store',
            'image_src': 'Image Src',
            'option1_name': 'Option1 Name',
            'option1_value': 'Option1 Value',
            'option2_name': 'Option2 Name',
            'option2_value': 'Option2 Value',
            'option3_name': 'Option3 Name',
            'option3_value': 'Option3 Value',
            'variant_price': 'Variant Price',
            'variant_compare_at_price': 'Variant Compare At Price',
            'track_inventory': 'Track Inventory',
            'allow_out_of_stock_purchases': 'Allow Out of Stock Purchases',
            'available_quantity': 'Available Quantity',
            'sku': 'SKU',
            'weight_value': 'Weight Value',
            'weight_unit': 'Weight Unit',
            'dimension_length': 'Dimension Length',
            'dimension_width': 'Dimension Width',
            'dimension_height': 'Dimension Height',
            'dimension_unit': 'Dimension Unit',
            'product_label_enable': 'Product Label Enable',
            'label_title': 'Label Title',
            'label_start_date': 'Label Start Date',
            'label_end_date': 'Label End Date',
            'seo_title': 'SEO Title',
            'seo_description': 'SEO Description'
        }

        # Renombrar columnas y seleccionar solo las que están en el mapeo
        df_clean = df_clean.rename(columns=ghl_mapping)
        
        # Columnas finales esperadas por GHL en el orden correcto
        ghl_columns_order = list(ghl_mapping.values())
        
        # Asegurarse de que todas las columnas de GHL existan, rellenando con NaN si no
        for col in ghl_columns_order:
            if col not in df_clean.columns:
                df_clean[col] = pd.NA

        # Seleccionar y reordenar las columnas
        df_clean = df_clean[ghl_columns_order]

        if df_clean.empty:
            raise HTTPException(status_code=400, detail="No quedan datos después de la limpieza.")

        # Convertir el DataFrame limpio a CSV en memoria
        output = io.StringIO()
        df_clean.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)

        return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8-sig')),
                                 media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=cleaned_products.csv"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")


@app.get("/")
async def read_root():
    return {"message": "Backend de limpieza de CSV funcionando"}