import streamlit as st
import os
import zipfile
from PIL import Image
from rembg import remove
import io

# Configuración de la página web
st.set_page_config(page_title="Remover Fondo en Masa", page_icon="✂️", layout="centered")

st.title("✂️ Eliminador de Fondos por Lote")
st.write("Sube múltiples imágenes para quitarles el fondo y colocarles un fondo blanco automáticamente.")

# Componente para subir múltiples archivos
uploaded_files = st.file_uploader("Arrastra tus imágenes aquí", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"📂 Se han cargado {len(uploaded_files)} imágenes.")
    
    # Botón para iniciar el proceso
    if st.button("🚀 Procesar imágenes ahora"):
        zip_buffer = io.BytesIO()
        
        # Crear un archivo ZIP en memoria
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, file in enumerate(uploaded_files):
                status_text.text(f"Procesando: {file.name} ({index + 1}/{len(uploaded_files)})")
                
                try:
                    # Leer y procesar imagen
                    input_image = Image.open(file).convert("RGB")
                    output_transparent = remove(input_image)
                    
                    # Crear lienzo blanco puro
                    white_bg = Image.new("RGBA", output_transparent.size, "WHITE")
                    final_image = Image.alpha_composite(white_bg, output_transparent.convert("RGBA"))
                    
                    # Guardar resultado en un buffer como JPEG
                    img_buffer = io.BytesIO()
                    final_image.convert("RGB").save(img_buffer, format="JPEG", quality=92)
                    img_buffer.seek(0)
                    
                    # Agregar al archivo ZIP
                    name, _ = os.path.splitext(file.name)
                    zipf.writestr(f"{name}_fondo_blanco.jpg", img_buffer.read())
                    
                except Exception as e:
                    st.error(f"Error con {file.name}: {str(e)}")
                
                # Actualizar barra de progreso
                progress_bar.progress((index + 1) / len(uploaded_files))
                
            status_text.text("✨ ¡Todo listo! Tu archivo está preparado.")
            
        zip_buffer.seek(0)
        
        # Botón de descarga del archivo ZIP comprimido
        st.download_button(
            label="📥 Descargar todas las imágenes (.ZIP)",
            data=zip_buffer,
            file_name="imagenes_fondo_blanco.zip",
            mime="application/zip"
        )
