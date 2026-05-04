import streamlit as st
import psycopg2
import os
from rembg import remove
from PIL import Image
import io

# 1. Configuração inicial (Deve ser a primeira linha)
st.set_page_config(page_title="Nexamente IA", layout="wide")

# 2. Inicializar variáveis de sessão para manter o login "travado"
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Função para conectar ao seu banco Postgres do Railway
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- BLOCO DE LOGIN ---
if not st.session_state["logado"]:
    st.title("Nexamente - Acesso")
    
    # Criamos um formulário de login isolado
    with st.form("login_form"):
        user = st.text_input("E-mail")
        pw = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")
        
        if entrar:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                # Verifica na tabela 'usuarios' que criamos
                cur.execute("SELECT nome FROM usuarios WHERE email=%s AND senha=%s", (user, pw))
                res = cur.fetchone()
                cur.close()
                conn.close()
                
                if res:
                    st.session_state["logado"] = True
                    st.session_state["nome"] = res[0]
                    st.rerun() # Recarrega o app já logado
                else:
                    st.error("Dados incorretos. Verifique seu acesso.")
            except Exception as e:
                st.error("Erro ao conectar ao banco. Verifique a DATABASE_URL.")
    
    st.stop() # Interrompe o código aqui se não estiver logado

# --- ÁREA DA FERRAMENTA (Só aparece após login bem-sucedido) ---
st.sidebar.success(f"Conectado: {st.session_state['nome']}")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.title("Removedor de Fundo Nexamente")
st.write("Selecione várias fotos para processar em lote.")

# 'accept_multiple_files=True' permite selecionar várias peças de uma vez
arquivos = st.file_uploader("Arraste suas fotos aqui", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if arquivos:
    # Processamos as imagens em uma lista para evitar que o clique no botão resete o estado
    if st.button("🚀 Iniciar Remoção em Massa"):
        for arquivo in arquivos:
            with st.status(f"Processando {arquivo.name}...", expanded=True):
                # Abrir imagem e processar com rembg
                img_original = Image.open(arquivo)
                img_sem_fundo = remove(img_original)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.image(img_original, caption="Original", use_container_width=True)
                with col2:
                    st.image(img_sem_fundo, caption="Sem Fundo", use_container_width=True)
                
                # Gerar botão de download para cada imagem
                buf = io.BytesIO()
                img_sem_fundo.save(buf, format="PNG")
                st.download_button(
                    label=f"Baixar {arquivo.name}",
                    data=buf.getvalue(),
                    file_name=f"sem_fundo_{arquivo.name}.png",
                    mime="image/png"
                )
            st.divider()
