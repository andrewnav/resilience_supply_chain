import duckdb
import os
import pandas as pd
import datetime

# Caminhos
INPUT_CSV = "data/bronze/raw/DataCoSupplyChainDataset.csv"
OUTPUT_SILVER = "data/silver/vendas_logistica.parquet"

def quality_check(df):
    """
    Executa testes de qualidade (Data Quality) no DataFrame.
    Impacto: Garante que a Gold receba apenas dados confiáveis.
    """
    print("🔍 Iniciando Auditoria de Saúde dos Dados...")
    
    erros = []
    
    # 1. Validação de Datas (Não pode haver data no futuro)
    hoje = pd.Timestamp.now()
    datas_futuras = df[df['data_pedido'] > hoje]
    if not datas_futuras.empty:
        erros.append(f"❌ Detectadas {len(datas_futuras)} linhas com datas futuras.")

    # 2. Validação Numérica (Vendas e Dias de Envio não podem ser negativos)
    negativos = df[df['valor_venda'] < 0]
    if not negativos.empty:
        erros.append(f"❌ Detectadas {len(negativos)} linhas com valor de venda negativo.")
        
    dias_invalidos = df[df['dias_envio_real'] < 0]
    if not dias_invalidos.empty:
        erros.append(f"❌ Detectados {len(dias_invalidos)} registros com dias de envio negativos.")

    # 3. Análise de Nulos (Categorias críticas)
    nulos = df['categoria'].isnull().sum()
    if nulos > 0:
        erros.append(f"⚠️ {nulos} registros sem categoria (serão tratados).")

    # 4. Relatório Final de Saúde
    if not erros:
        print("✅ Saúde dos dados aprovada! 100% de integridade.")
    else:
        for erro in erros:
            print(erro)
            
    return df[df['valor_venda'] >= 0] # Filtro de sobrevivência: removemos o que é lixo

def process_silver_layer():
    print("🦆 Camada Silver: Limpeza e Normalização COMPLETA...")
    os.makedirs("data/silver", exist_ok=True)
    
    # --- BUSCANDO DADO EXTERNO (BRONZE) ---
    PATH_CONTEXTO = "data/bronze/contexto_externo.parquet"
    preco_brent = 0.0 # Valor padrão caso o arquivo não exista
    
    if os.path.exists(PATH_CONTEXTO):
        df_ctx = pd.read_parquet(PATH_CONTEXTO)
        # Pega o primeiro valor da coluna 'valor' (Brent)
        preco_brent = round(float(df_ctx['valor'].iloc[0]), 2)
        print(f"📊 Preço do Petróleo Brent recuperado: ${preco_brent}")
    else:
        print("⚠️ Aviso: Arquivo de contexto não encontrado. Usando 0.0.")

    try:
        # 1. Leitura do CSV com encoding apropriado
        print(f"📖 Lendo arquivo em: {INPUT_CSV}")
        df_raw = pd.read_csv(INPUT_CSV, encoding='latin1', on_bad_lines='skip')

        # Limpeza de Headers: Remove espaços extras e caracteres invisíveis
        df_raw.columns = [col.strip() for col in df_raw.columns]
        
        print(f"📋 Colunas disponíveis no CSV: {df_raw.columns.tolist()[:10]}...")
        
        # 2. Conectamos o DuckDB ao DataFrame do Pandas
        con = duckdb.connect()
        
        # ✅ AGORA COM TODAS AS COLUNAS NECESSÁRIAS
        df_cleaned = con.execute(f"""
            SELECT 
                -- Produto
                "Category Name" AS categoria,
                "Product Name" AS nome_produto,
                
                -- Cliente (Geografia completa)
                "Customer City" AS cliente_cidade,
                "Customer State" AS cliente_estado,
                "Customer Country" AS cliente_pais,
                
                -- Pedido (Geografia)
                "Order City" AS pedido_cidade,
                "Order State" AS pedido_estado,
                "Order Country" AS pedido_pais,
                "Order Region" AS pedido_regiao,
                
                -- Logística
                "Delivery Status" AS status_entrega,
                "Shipping Mode" AS modo_envio,
                CAST("Days for shipping (real)" AS INTEGER) AS dias_envio_real,
                CAST("Days for shipment (scheduled)" AS INTEGER) AS dias_envio_agendado,
                
                -- Temporal
                "order date (DateOrders)" AS data_pedido,
                "shipping date (DateOrders)" AS data_envio,
                
                -- Financeiro
                CAST("Order Item Total" AS DOUBLE) AS valor_venda,
                CAST("Order Profit Per Order" AS DOUBLE) AS lucro_pedido,
                CAST("Sales per customer" AS DOUBLE) AS venda_por_cliente,
                CAST("Benefit per order" AS DOUBLE) AS beneficio_pedido,
                
                -- Contexto Externo (Petróleo Brent)
                {preco_brent} AS preco_petroleo_brent,
                
                -- IDs originais (úteis para rastreamento)
                "Order Id" AS id_pedido_original,
                "Product Card Id" AS id_produto_original,
                "Customer Id" AS id_cliente_original
                
            FROM df_raw 
        """).df()

        # 3. Conversão de datas e tratamento
        df_cleaned['data_pedido'] = pd.to_datetime(df_cleaned['data_pedido'], errors='coerce')
        df_cleaned['data_envio'] = pd.to_datetime(df_cleaned['data_envio'], errors='coerce')
        
        # Tratamento de nulos em campos críticos
        df_cleaned['categoria'] = df_cleaned['categoria'].fillna('Sem Categoria')
        df_cleaned['nome_produto'] = df_cleaned['nome_produto'].fillna('Produto Desconhecido')
        df_cleaned['cliente_pais'] = df_cleaned['cliente_pais'].fillna('Desconhecido')
        df_cleaned['cliente_estado'] = df_cleaned['cliente_estado'].fillna('N/A')
        df_cleaned['dias_envio_agendado'] = df_cleaned['dias_envio_agendado'].fillna(0)
        df_cleaned['dias_envio_real'] = df_cleaned['dias_envio_real'].fillna(0)
        
        # Auditoria de Qualidade
        df_final = quality_check(df_cleaned)

        # 4. Salvando em Parquet
        df_final.to_parquet(OUTPUT_SILVER, index=False)
        
        print(f"\n✅ Silver concluída com SUCESSO!")
        print(f"📊 Registros processados: {len(df_final):,}")
        print(f"🌍 Países únicos: {df_final['cliente_pais'].nunique()}")
        print(f"📦 Categorias: {df_final['categoria'].nunique()}")
        print(f"📍 Cidades: {df_final['cliente_cidade'].nunique()}")
        print(f"\n💾 Arquivo salvo em: {OUTPUT_SILVER}")

    except Exception as e:
        print(f"❌ Erro crítico na Silver: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_silver_layer()