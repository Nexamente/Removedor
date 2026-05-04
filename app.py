import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
import os

st.set_page_config(page_title="Presence - Processamento em Lote", layout="wide")

st.title("📦 Processador de Produtos em Lote")
st.write("Suba várias fotos e baixe todas limpas em um único arquivo ZIP.")

# Upload de múltiplos arquivos
uploaded_files = st.file_uploader("Arraste as fotos dos produtos aqui...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Criar um buffer para armazenar o arquivo ZIP na memória
    zip_buffer = io.BytesIO()
    
    # Criar o arquivo ZIP
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        
        st.write(f"Processando {len(uploaded_files)} imagens...")
        barra_progresso = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            # Processamento de cada imagem
            input_image = file.read()
            output_image = remove(input_image)
            
            # Definir nome do arquivo dentro do ZIP
            nome_limpo = f"{os.path.splitext(file.name)[0]}_sem_fundo.png"
            
            # Adicionar a imagem processada ao ZIP
            zip_file.writestr(nome_limpo, output_image)
            
            # Atualizar barra de progresso
            progresso = (i + 1) / len(uploaded_files)
            barra_progresso.progress(progresso)

    st.success("✅ Todas as imagens foram processadas!")

    # Botão de download do ZIP completo
    st.download_button(
        label="🚀 Baixar todas as imagens (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="produtos_limpos.zip",
        mime="application/zip"
    )