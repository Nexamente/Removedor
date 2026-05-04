import os
from rembg import remove
from tqdm import tqdm

def processar():
    pasta_in = 'entrada'
    pasta_out = 'saida'

    # Verifica se as pastas existem
    if not os.path.exists(pasta_in):
        os.makedirs(pasta_in)
        print("Pasta 'entrada' criada. Coloque as fotos nela e rode de novo.")
        return

    if not os.path.exists(pasta_out):
        os.makedirs(pasta_out)

    arquivos = [f for f in os.listdir(pasta_in) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"Localizados {len(arquivos)} arquivos para processar.")

    for arquivo in tqdm(arquivos, desc="Removendo fundo"):
        caminho_input = os.path.join(pasta_in, arquivo)
        nome_limpo = os.path.splitext(arquivo)[0] + ".png"
        caminho_output = os.path.join(pasta_out, nome_limpo)

        with open(caminho_input, 'rb') as i:
            input_data = i.read()
            output_data = remove(input_data)
        
        with open(caminho_output, 'wb') as o:
            o.write(output_data)

if __name__ == "__main__":
    processar()
