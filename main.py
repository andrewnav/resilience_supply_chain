import sys
import os

# pasta raiz ao caminho de busca do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Importar suas funções de pipeline
from src.extract.kaggle_api import download_supply_chain_data
from src.extract.context_api import get_brent_oil_price_api
from src.transform.silver_layer import process_silver_layer
from src.transform.gold_layer import create_gold_layer_complete

import subprocess
import time
from pyngrok import ngrok
from dotenv import load_dotenv



def run_pipeline():
    print("🚀 Iniciando Pipeline de Dados...")
    get_brent_oil_price_api() 
    download_supply_chain_data() # Bronze
    process_silver_layer()  # Silver
    create_gold_layer_complete() # Gold
    print("✅ Pipeline concluído com sucesso!")

def start_dashboard():
    load_dotenv()
    token = os.getenv("NGROK_AUTH_TOKEN")
    
    if not token:
        print("❌ Erro: NGROK_AUTH_TOKEN não configurado.")
        return

    ngrok.set_auth_token(token)
    
    print("📊 Iniciando Dashboard e Túnel...")
    # Lança o streamlit
    proc = subprocess.Popen([
    "streamlit", 
    "run", 
    "app/dashboard.py", 
    "--browser.gatherUsageStats=false", # Desativar coleta de dados
    "--server.headless=true"            # Evita abrir o browser automaticamente (o Ngrok já faz o papel de link)
])
    
    time.sleep(3) # Tempo para o streamlit "respirar"
    
    public_url = ngrok.connect(8501)
    print(f"\n🔗 ACESSO PÚBLICO: {public_url.public_url}\n")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        ngrok.kill()
        proc.terminate()

if __name__ == "__main__":
    # 1. Primeiro garante que os dados estão prontos
    run_pipeline()
    
    # 2. Depois sobe a interface
    start_dashboard()