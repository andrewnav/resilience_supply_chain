import kagglehub
import shutil
import os

def download_supply_chain_data():
    """
    Utiliza o kagglehub para baixar a versão mais recente do dataset.
    Vantagem: Mais rápido, moderno e lida melhor com grandes volumes.
    """
    print("🚀 Iniciando download via kagglehub...")
    
    # Identificador do dataset (o mesmo do Kaggle)
    handle = "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis"
    
    try:
        # O kagglehub baixa para um cache local e retorna o caminho
        path = kagglehub.dataset_download(handle)
        
        print(f"✅ Arquivos baixados em cache: {path}")
        
        # Como queremos manter nosso projeto organizado (Arquitetura Medalhão),
        # vamos mover os arquivos do cache do kagglehub para nossa pasta data/bronze/raw
        dest_path = "data/bronze/raw"
        os.makedirs(dest_path, exist_ok=True)
        
        for item in os.listdir(path):
            s = os.path.join(path, item)
            d = os.path.join(dest_path, item)
            if os.path.isfile(s):
                shutil.copy2(s, d) # Copia os arquivos para nossa estrutura
        
        print(f"🎯 Dados movidos com sucesso para: {dest_path}")
        return dest_path

    except Exception as e:
        print(f"❌ Erro ao baixar dataset: {e}")
        return None

if __name__ == "__main__":
    download_supply_chain_data()