from fastapi import FastAPI, Request, HTTPException
import psycopg2
import os
import uvicorn

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.post("/webhook")
async def hotmart_webhook(request: Request):
    try:
        data = await request.json()
        
        # Extraindo dados básicos (ajuste conforme o JSON da Hotmart)
        email = data.get('data', {}).get('buyer', {}).get('email')
        nome = data.get('data', {}).get('buyer', {}).get('name')
        status = data.get('event') # Ex: PURCHASE_APPROVED

        if status == "PURCHASE_APPROVED" and email:
            conn = get_db_connection()
            cur = conn.cursor()
            # Salva ou atualiza o usuário para ter acesso ao Nexamente
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s) "
                "ON CONFLICT (email) DO NOTHING",
                (nome, email, "mudar123") # Senha padrão inicial
            )
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success"}
        
        return {"status": "ignored"}
    except Exception as e:
        print(f"Erro no Webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # O comando correto para iniciar o FastAPI programaticamente
    uvicorn.run(app, host="0.0.0.0", port=port)
