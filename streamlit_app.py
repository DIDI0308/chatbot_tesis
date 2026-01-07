import streamlit as st
from docx import Document

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador Simple", page_icon="🔎")

# --- FUNCIÓN: LEER DOCUMENTO ---
def procesar_docx_simple(file):
    doc = Document(file)
    datos = []
    
    # 1. Párrafos
    for para in doc.paragraphs:
        texto = para.text.strip()
        if len(texto) > 20: # Ignorar textos muy cortos
            datos.append(texto)
            
    # 2. Tablas
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                datos.append(" | ".join(row_text))
    return datos

# --- FUNCIÓN: BUSCAR POR PALABRAS CLAVE ---
def buscar_coincidencia(pregunta, lista_textos):
    pregunta = pregunta.lower()
    palabras_clave = pregunta.split()
    
    mejor_texto = None
    mayor_acierto = 0
    
    for texto in lista_textos:
        texto_lower = texto.lower()
        aciertos = 0
        
        # Contamos cuántas palabras de la pregunta aparecen en este párrafo
        for palabra in palabras_clave:
            # Ignoramos palabras comunes muy cortas (como "el", "la", "y") para mejorar precisión
            if len(palabra) > 3 and palabra in texto_lower:
                aciertos += 1
        
        if aciertos > mayor_acierto:
            mayor_acierto = aciertos
            mejor_texto = texto
            
    return mejor_texto, mayor_acierto

# --- INTERFAZ ---
st.title("🔎 Buscador de Tesis (Básico)")
st.caption("Sube tu Word. El sistema buscará el párrafo que contenga más palabras de tu pregunta.")

uploaded_file = st.file_uploader("Sube tu archivo .docx", type=['docx'])

if uploaded_file is not None:
    # Procesar archivo
    if "textos_doc" not in st.session_state:
        try:
            st.session_state.textos_doc = procesar_docx_simple(uploaded_file)
            st.success(f"✅ Archivo leído correctamente ({len(st.session_state.textos_doc)} fragmentos).")
        except Exception as e:
            st.error(f"Error leyendo el archivo: {e}")

    # Chat
    if pregunta := st.chat_input("Escribe tu pregunta..."):
        
        # Mostrar usuario
        with st.chat_message("user"):
            st.write(pregunta)
            
        # Buscar
        if "textos_doc" in st.session_state:
            respuesta, aciertos = buscar_coincidencia(pregunta, st.session_state.textos_doc)
            
            with st.chat_message("assistant"):
                if respuesta and aciertos > 0:
                    st.markdown("### Lo que encontré en el documento:")
                    st.info(respuesta)
                    st.caption(f"Coincidencia por palabras clave: {aciertos} palabras encontradas.")
                else:
                    st.warning("No encontré ningún párrafo que contenga esas palabras clave. Intenta usar términos más específicos del documento.")
