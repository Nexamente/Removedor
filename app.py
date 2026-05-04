import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# 1. Configuração da página (Sempre a primeira linha)
st.set_page_config(page_title="Nexamente - IA", layout="wide")

# 2. Inicialização do estado de login
if "logado" not in st.session_state:
    st.session_state["logado"] = False

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- FUNÇÃO DE LOGIN ---
def realizar_login(email, senha):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM usuarios WHERE email=%s AND senha=%s", (email, senha))
        resultado = cur.fetchone()
        cur.close()
        conn.close()
        if resultado:
            st.session_state["logado"] = True
            st.session_state["nome_usuario"] = resultado[0]
            return True
        return False
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

# --- INTERFACE ---

# Se não estiver logado, mostra o formulário
if not st.session_state["logado"]:
    st.title("Nexamente - Acesso")
    email_input = st.text_input("E-mail")
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if realizar_login(email_input, senha_input):
            st.rerun() # Aqui ele recarrega e já pula para a ferramenta
        else:
            st.error("Usuário ou senha inválidos.")
    st.stop() # Bloqueia tudo abaixo enquanto não logar

# --- DAQUI PARA BAIXO É A FERRAMENTA ---
# O Streamlit só vai ler isso se 'st.session_state["logado"]' for True

st.sidebar.success(f"Olá, {st.session_state['nome_usuario']}!")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.title("Nexamente - Removedor de Fundo")

# IMPORTANTE: Coloque 'accept_multiple_files=True' para as peças da Presence Motos
arquivos = st.file_uploader("Arraste suas fotos aqui", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if arquivos:
    # Use um botão para disparar o processamento
    if st.button("Processar Imagens"):
        for arquivo in arquivos:
            with st.spinner(f"Limpando {arquivo.name}..."):
                img = Image.open(arquivo)
                saida = remove(img) # rembg direto na imagem aberta
                
                col1, col2 = st.columns(2)
                col1.image(img, caption="Original", width=300)
                col2.image(saida, caption="Sem Fundo", width=300)
                
                # Preparar download
                buf = io.BytesIO()
                saida.save(buf, format="PNG")
                st.download_button(f"Baixar {arquivo.name}", buf.getvalue(), f"limpa_{arquivo.name}.png", "image/png")
            st.divider()
