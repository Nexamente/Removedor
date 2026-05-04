import streamlit as st
import psycopg2
import os
from rembg import remove, new_session
from PIL import Image
import io

# 1. Configuração inicial - Sempre a primeira
st.set_page_config(page_title="Nexamente IA", layout="wide")

# 2. Inicialização do Cadeado de Sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# 3. Criar uma sessão única para a IA (economiza muita RAM)
if "rembg_session" not in st.session_state:
    st.session_state["rembg_session"] = new_session()

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- INTERFACE DE LOGIN ---
if not st.session_state["logado"]:
    st.title("Nexamente - Acesso")
    
    # Usamos o st.form para evitar que a página recarregue a cada letra digitada
    with st.form("form_acesso"):
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
                    st.rerun() # Trava o login e pula para a ferramenta
                else:
                    st.error("Dados incorretos.")
            except:
                st.error("Erro de conexão com o banco.")
    st.stop() # Bloqueia o restante do código

# --- ÁREA DA FERRAMENTA (SÓ RODA SE LOGADO) ---
st.sidebar.success(f"Olá, {st.session_state['nome']}!")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.title("Removedor de Fundo Nexamente")

# Seleção múltipla habilitada
arquivos = st.file_uploader("Suba as fotos das peças", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if arquivos:
    if st.button("🚀 Iniciar Remoção Profissional"):
        for arquivo in arquivos:
            with st.status(f"Processando {arquivo.name}...", expanded=True):
                img = Image.open(arquivo)
                
                # O SEGREDO: Usamos a sessão fixa para não estourar a RAM
                saida = remove(
                    img, 
                    session=st.session_state["rembg_session"],
                    post_process_mask=True # Com 8GB você pode usar qualidade máxima
                )
                
                col1, col2 = st.columns(2)
                col1.image(img, caption="Original", width=300)
                col2.image(saida, caption="Sem Fundo", width=300)
                
                # Botão de download
                buf = io.BytesIO()
                saida.save(buf, format="PNG")
                st.download_button(f"Baixar {arquivo.name}", buf.getvalue(), f"limpa_{arquivo.name}.png")
            st.divider()
