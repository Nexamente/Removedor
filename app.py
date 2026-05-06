import streamlit as st
import psycopg2
import os
from rembg import remove, new_session
from PIL import Image
import io
import zipfile  # Import necessário para o ZIP

# 1. Configuração inicial
st.set_page_config(page_title="Nexamente IA", layout="wide")

# 2. Inicialização do Estado da Sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "rembg_session" not in st.session_state:
    st.session_state["rembg_session"] = new_session()

# Criamos uma lista para guardar as imagens processadas e permitir o download do ZIP
if "imagens_processadas" not in st.session_state:
    st.session_state["imagens_processadas"] = []

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- INTERFACE DE LOGIN ---
if not st.session_state["logado"]:
    st.title("Nexamente - Acesso")
    
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
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
            except:
                st.error("Erro de conexão com o banco de dados. Verifique a DATABASE_URL.")
    st.stop()

# --- ÁREA DA FERRAMENTA ---
st.sidebar.success(f"Olá, {st.session_state['nome']}!")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.session_state["imagens_processadas"] = [] # Limpa ao sair
    st.rerun()

st.title("Removedor de Fundo Nexamente")

arquivos = st.file_uploader("Suba as fotos das peças", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if arquivos:
    # Botão para processar
    if st.button("🚀 Iniciar Remoção Profissional"):
        st.session_state["imagens_processadas"] = [] # Reseta a lista para um novo lote
        
        for arquivo in arquivos:
            with st.status(f"Processando {arquivo.name}...", expanded=False) as status:
                img = Image.open(arquivo)
                
                # Remoção de fundo
                saida = remove(
                    img, 
                    session=st.session_state["rembg_session"],
                    post_process_mask=True
                )
                
                # Salva na lista da sessão para o ZIP
                st.session_state["imagens_processadas"].append({
                    "nome": f"limpa_{arquivo.name}.png",
                    "imagem": saida
                })
                
                col1, col2 = st.columns(2)
                col1.image(img, caption="Original", width=300)
                col2.image(saida, caption="Sem Fundo", width=300)
                status.update(label=f"Concluído: {arquivo.name}", state="complete")

    # --- BOTÃO DE ZIP (Aparece se houver imagens processadas) ---
    if st.session_state["imagens_processadas"]:
        st.divider()
        st.subheader("📦 Finalizar Download")
        
        # Cria o arquivo ZIP na memória
        buffer_zip = io.BytesIO()
        with zipfile.ZipFile(buffer_zip, "w") as zf:
            for item in st.session_state["imagens_processadas"]:
                buf_img = io.BytesIO()
                item["imagem"].save(buf_img, format="PNG")
                zf.writestr(item["nome"], buf_img.getvalue())
        
        st.download_button(
            label="📥 BAIXAR TODAS AS FOTOS EM ZIP",
            data=buffer_zip.getvalue(),
            file_name="fotos_sem_fundo_nexamente.zip",
            mime="application/zip",
            use_container_width=True
        )
