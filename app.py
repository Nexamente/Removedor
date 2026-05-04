import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# 1. Configurações Iniciais
st.set_page_config(page_title="Nexamente - IA", layout="wide")

# Função de conexão com o banco
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Sistema de Login
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("Nexamente - Acesso")
    with st.form("login_form"):
        user = st.text_input("E-mail")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT nome FROM usuarios WHERE email=%s AND senha=%s", (user, pw))
                resultado = cur.fetchone()
                cur.close()
                conn.close()
                if resultado:
                    st.session_state["logado"] = True
                    st.session_state["nome"] = resultado[0]
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
            except Exception as e:
                st.error("Erro ao conectar ao banco de dados.")
    st.stop()

# Área da Ferramenta
st.title(f"Bem-vindo ao Nexamente, {st.session_state['nome']}!")
arquivo = st.file_uploader("Suba sua imagem", type=["jpg", "png", "jpeg"])

if arquivo:
    imagem = Image.open(arquivo)
    with st.spinner("Removendo fundo..."):
        img_io = io.BytesIO()
        imagem.save(img_io, format='PNG')
        saida = remove(img_io.getvalue())
        img_final = Image.open(io.BytesIO(saida))
        st.image(img_final)
        
        buf = io.BytesIO()
        img_final.save(buf, format="PNG")
        st.download_button("Baixar Resultado", buf.getvalue(), "resultado.png", "image/png")
