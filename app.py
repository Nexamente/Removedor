import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
import os
import psycopg2 # Biblioteca para conectar ao banco de dados

# Função para verificar se o usuário existe no banco de dados do Railway
def verificar_login(usuario, senha):
    conn = psycopg2.connect(st.secrets["DATABASE_URL"]) # Puxa a conexão automática do Railway
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email=%s AND senha=%s", (usuario, senha))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado

# Interface de Login
st.title("Nexamente - Acesso Restrito")
user_input = st.text_input("E-mail (usuário Hotmart)")
pass_input = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if verificar_login(user_input, pass_input):
        st.session_state["logado"] = True
        st.success("Login realizado com sucesso!")
    else:
        st.error("Usuário não encontrado ou compra ainda não processada.")

if not st.session_state.get("logado"):
    st.stop() # Trava o resto do app se não estiver logado

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
