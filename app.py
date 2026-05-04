import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# Configurações Iniciais
st.set_page_config(page_title="Nexamente - IA", layout="wide")

# Função de conexão com o banco
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- CONTROLE DE SESSÃO (ESSENCIAL) ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome" not in st.session_state:
    st.session_state["nome"] = ""

# Tela de Login
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
                    st.rerun() # Força o recarregamento já logado
                else:
                    st.error("Dados incorretos.")
            except Exception as e:
                st.error("Erro ao conectar ao banco de dados.")
    st.stop()

# --- ÁREA DA FERRAMENTA (SÓ CHEGA AQUI SE LOGADO) ---
st.title(f"Painel Nexamente - Olá, {st.session_state['nome']}!")

# 'accept_multiple_files=True' resolve o problema de selecionar várias
arquivos = st.file_uploader("Selecione as imagens dos produtos", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if arquivos:
    st.write(f"Você selecionou {len(arquivos)} imagens.")
    
    if st.button("Remover Fundo de Todas"):
        for i, arquivo in enumerate(arquivos):
            with st.container():
                col1, col2 = st.columns(2)
                imagem = Image.open(arquivo)
                
                with col1:
                    st.image(imagem, caption=f"Original {i+1}", width=250)
                
                with col2:
                    with st.spinner(f"Processando imagem {i+1}..."):
                        img_io = io.BytesIO()
                        imagem.save(img_io, format='PNG')
                        saida = remove(img_io.getvalue())
                        img_final = Image.open(io.BytesIO(saida))
                        st.image(img_final, caption=f"Sem fundo {i+1}", width=250)
                        
                        # Botão de download individual
                        buf = io.BytesIO()
                        img_final.save(buf, format="PNG")
                        st.download_button(f"Baixar Imagem {i+1}", buf.getvalue(), f"resultado_{i+1}.png", "image/png")
                st.divider()
