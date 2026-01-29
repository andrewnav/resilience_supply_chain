import yfinance as yf
import pandas as pd
import datetime
import os

# Caminho para a camada Bronze
OUTPUT_PATH = "data/bronze/contexto_externo.parquet"

def get_brent_oil_price_api():
    """
    Consome a API do Yahoo Finance via yfinance para capturar o preço do Petróleo Brent.
    Impacto: Alta confiabilidade, baixa latência e sem necessidade de renderização de browser.
    """
    print("🚀 Iniciando extração via API (yfinance)...")
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    try:
        # Ticker do Petróleo Brent na Yahoo Finance: BZ=F (Futures)
        brent = yf.Ticker("BZ=F")
        
        # Pega o preço de fechamento mais recente
        data = brent.history(period="1d")
        
        if not data.empty:
            price_value = float(data['Close'].iloc[-1])
            print(f"📊 Preço do Brent via API: ${price_value:.2f}")

            # Criar DataFrame para a Bronze
            df_context = pd.DataFrame({
                "data_coleta": [datetime.datetime.now()],
                "indicador": ["Petroleo_Brent"],
                "valor": [price_value],
                "moeda": ["USD"],
                "fonte": ["Yahoo_Finance_API"]
            })

            # Salvar em Parquet
            df_context.to_parquet(OUTPUT_PATH, index=False)
            print(f"✅ Dados salvos com sucesso em: {OUTPUT_PATH}")
        else:
            print("⚠️ Nenhum dado retornado pela API.")

    except Exception as e:
        print(f"❌ Erro ao acessar API Financeira: {e}")

if __name__ == "__main__":
    get_brent_oil_price_api()