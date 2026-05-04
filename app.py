import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# 1. Configurações Iniciais - DEVE ser a primeira coisa
st.set_page_config(page_title="Nexamente - IA", layout="wide")

# 2. Inicialização do Session State (A trava de segurança)
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_usuario" not in st.session_state:
    st.session_state["nome_usuario"] = ""

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- LÓGICA DE NAVEGAÇÃO ---

# SE NÃO ESTIVER LOGADO, MOSTRA APENAS O LOGIN
if not st.session_state["logado"]:
    st.title("Nexamente - Acesso Restrito")
    
    with st.container():
        user = st.text_input("E-mail registrado")
        pw = st.text_input("Senha", type="password")
        
        if st.button("Acessar Painel"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT nome FROM usuarios WHERE email=%s AND senha=%s", (user, pw))
                resultado = cur.fetchone()
                cur.close()
                conn.close()
                
                if resultado:
                    st.session_state["logado"] = True
                    st.session_state["nome_usuario"] = resultado[0]
                    st.rerun() # RECARREGA JÁ COMO LOGADO
                else:
                    st.error("E-mail ou senha incorretos.")
            except Exception as e:
                st.error("Erro técnico ao conectar. Verifique a DATABASE_URL.")
    
    st.stop() # PARA O SCRIPT AQUI SE NÃO LOGAR

# --- SE CHEGOU AQUI, É PORQUE ESTÁ LOGADO ---
# Tudo daqui para baixo é a ferramenta de remoção

st.sidebar.success(f"Logado como: {st.session_state['nome_usuario']}")
if st.sidebar.button("Encerrar Sessão"):
    st.session_state["logado"] = False
    st.rerun()

st.title("Nexamente - Processamento de Imagens")

# O restante do seu código de upload (accept_multiple_files=True) e remoção vai aqui...

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
