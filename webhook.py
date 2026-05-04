from fastapi import FastAPI, Request, BackgroundTasks
import psycopg2
import os

app = FastAPI()

# Pega o link do banco de dados que o Railway te dá automaticamente
DATABASE_URL = os.environ.get('DATABASE_URL')

def salvar_cliente_no_banco(email, nome):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Cria a tabela se não existir (ID, Email, Senha, Nome)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT
            )
        """)
        # A senha padrão será os 4 primeiros dígitos do email + '123' 
        # (Você pode mudar essa lógica)
        senha_padrao = email.split('@')[0][:4] + "123"
        
        cur.execute("INSERT INTO usuarios (email, senha, nome) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    (email, senha_padrao, nome))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

@app.post("/hotmart-webhook")
async def hotmart_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # Verifica se a compra foi aprovada
    status = data.get('event') # A Hotmart envia o tipo de evento aqui
    
    if status == "PURCHASE_APPROVED":
        email = data['data']['buyer']['email']
        nome = data['data']['buyer']['name']
        
        # Salva no banco sem travar a resposta da Hotmart
        background_tasks.add_task(salvar_cliente_no_banco, email, nome)
        
    return {"status": "ok"}
