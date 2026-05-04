import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# 1. Configurações Iniciais do Nexamente
st.set_page_config(page_title="Nexamente - IA", layout="wide")

# Função para conectar ao banco de dados usando a variável que você configurou
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Função para verificar se o cliente existe no banco
def verificar_login(usuario, senha):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM usuarios WHERE email=%s AND senha=%s", (usuario, senha))
        resultado = cur.fetchone()
        cur.close()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro de conexão com o banco: {e}")
        return None

# --- SISTEMA DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("Nexamente - Login")
    with st.form("login_form"):
        user = st.text_input("E-mail de compra")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("Acessar Sistema"):
            dados = verificar_login(user, pw)
            if dados:
                st.session_state["logado"] = True
                st.session_state["nome"] = dados[0]
                st.rerun()
            else:
                st.error("Usuário não encontrado. Verifique se o pagamento foi aprovado.")
    st.stop()

# --- ÁREA DO CLIENTE (Só aparece após login) ---
st.sidebar.write(f"Conectado como: **{st.session_state['nome']}**")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.title("Nexamente - Removedor de Fundo Profissional")
st.write("Suba sua foto e deixe nossa IA trabalhar para você.")

arquivo_upload = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])

if arquivo_upload is not None:
    imagem = Image.open(arquivo_upload)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        st.image(imagem, use_column_width=True)
    
    with st.spinner("Processando com IA Nexamente..."):
        # Processamento da imagem
        img_array = io.BytesIO()
        imagem.save(img_array, format='PNG')
        resultado_bytes = remove(img_array.getvalue())
        imagem_final = Image.open(io.BytesIO(resultado_bytes))
        
    with col2:
        st.subheader("Resultado")
        st.image(imagem_final, use_column_width=True)
        
        # Botão de Download
        buf = io.BytesIO()
        imagem_final.save(buf, format="PNG")
        st.download_button(
            label="Baixar Imagem Sem Fundo",
            data=buf.getvalue(),
            file_name="nexamente_resultado.png",
            mime="image/png"
        )
