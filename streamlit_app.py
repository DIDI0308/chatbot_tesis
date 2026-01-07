import streamlit as st
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador Tesis Offline", page_icon="🔍")

# --- FUNCIÓN: LEER DOCUMENTO Y DIVIDIR EN PÁRRAFOS ---
def procesar_docx(uploaded_file):
    doc = Document(uploaded_file)
    chunks = []
    
    # 1. Extraer párrafos con texto real
    for para in doc.paragraphs:
        texto = para.text.strip()
        if len(texto) > 30: # Filtramos párrafos muy cortos (títulos vacíos, firmas, etc.)
            chunks.append(texto)
            
    # 2. Extraer tablas
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                texto_tabla = " | ".join(row_text)
                if len(texto_tabla) > 20:
                    chunks.append(f"[Tabla]: {texto_tabla}")
    
    return chunks

# --- FUNCIÓN: BUSCAR LA MEJOR COINCIDENCIA ---
def encontrar_respuesta(pregunta, lista_textos):
    # Agregamos la pregunta a la lista de textos para compararla
    textos_a_comparar = [pregunta] + lista_textos
    
    # Convertir texto a números (Vectores TF-IDF)
    vectorizer = TfidfVectorizer().fit_transform(textos_a_comparar)
    vectors = vectorizer.toarray()
    
    # El vector 0 es la pregunta, el resto son los párrafos del doc
    csim = cosine_similarity(vectors[0:1], vectors[1:])
    
    # Obtener el índice del párrafo con mayor similitud
    mejor_indice = csim.argmax()
    score = csim[0][mejor_indice]
    
    # Si la coincidencia es muy baja (menor a 0.1), probablemente no hay respuesta
    if score < 0.1:
        return None, 0
        
    return lista_textos[mejor_indice], score

# --- INTERFAZ ---
st.title("🔍 Buscador Tesis (Sin IA)")
st.markdown("""
Este sistema no usa IA (GPT). Busca matemáticamente el párrafo de tu documento 
que más se parece a tu pregunta. **Es 100% gratis y offline.**
""")

# Carga de archivo
uploaded_file = st.file_uploader("Sube tu Tesis/Documento (.docx)", type=['docx'])

# Lógica principal
if uploaded_file is not None:
    # Procesar solo una vez
    if "db_textos" not in st.session_state:
        with st.spinner("Procesando documento..."):
            st.session_state.db_textos = procesar_docx(uploaded_file)
        st.success(f"✅ Documento indexado. Se encontraron {len(st.session_state.db_textos)} fragmentos.")

    # Chat input
    if pregunta := st.chat_input("Escribe tu pregunta exacta..."):
        
        # Mostrar pregunta usuario
        with st.chat_message("user"):
            st.markdown(pregunta)
            
        # Buscar respuesta
        respuesta, score = encontrar_respuesta(pregunta, st.session_state.db_textos)
        
        # Mostrar respuesta sistema
        with st.chat_message("assistant"):
            if respuesta:
                st.markdown(f"**Encontré esto en el documento** (Coincidencia: {int(score*100)}%):")
                st.info(respuesta)
            else:
                st.warning("No encontré ningún párrafo en el documento que hable de eso. Intenta usar palabras clave específicas.")

else:
    # Limpiar memoria si quitan el archivo
    if "db_textos" in st.session_state:
        del st.session_state.db_textos
