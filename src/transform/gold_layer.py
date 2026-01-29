import duckdb
import os

INPUT_SILVER = "data/silver/vendas_logistica.parquet"
OUTPUT_GOLD_DIR = "data/gold"

def create_gold_layer_complete():
    """
    Cria Star Schema COMPLETO com 5 dimensões + 1 fato
    
    Dimensões:
    1. dim_tempo - Datas completas (ano, mês, dia, data_completa)
    2. dim_logistica - Status, modo, dias real/agendado
    3. dim_produtos - Categoria + Nome do produto
    4. dim_clientes - Cidade, Estado, País
    5. dim_contexto - Petróleo Brent
    
    Fato:
    - fact_vendas - Relaciona todas as dimensões + métricas
    """
    
    print("🏗️ Construindo Star Schema COMPLETO com TODAS as colunas...")
    os.makedirs(OUTPUT_GOLD_DIR, exist_ok=True)
    con = duckdb.connect()

    try:
        # Criar view da camada Silver
        con.execute(f"CREATE VIEW silver_data AS SELECT * FROM read_parquet('{INPUT_SILVER}')")
        
        # Verificar se Silver tem dados
        row_count = con.execute("SELECT COUNT(*) FROM silver_data").fetchone()[0]
        print(f"📊 Total de registros na Silver: {row_count:,}")
        
        if row_count == 0:
            print("❌ ERRO: Silver está vazia! Execute silver_layer.py primeiro.")
            return

        # ========================================================================
        # 1. DIMENSÃO TEMPO - Com data completa + componentes
        # ========================================================================
        print("\n📅 1/5 - Criando dim_tempo...")
        con.execute(f"""
            COPY (
                SELECT DISTINCT 
                    data_pedido AS id_tempo,
                    data_pedido AS data_completa,
                    EXTRACT(YEAR FROM data_pedido) AS ano,
                    EXTRACT(MONTH FROM data_pedido) AS mes,
                    EXTRACT(DAY FROM data_pedido) AS dia,
                    EXTRACT(DOW FROM data_pedido) AS dia_semana,
                    EXTRACT(QUARTER FROM data_pedido) AS trimestre
                FROM silver_data 
                WHERE data_pedido IS NOT NULL
                ORDER BY data_pedido
            ) TO '{OUTPUT_GOLD_DIR}/dim_tempo.parquet' (FORMAT PARQUET)
        """)
        
        tempo_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_tempo.parquet')").fetchone()[0]
        print(f"   ✅ {tempo_count:,} datas únicas criadas")

        # ========================================================================
        # 2. DIMENSÃO LOGÍSTICA - Status + Modo + Dias
        # ========================================================================
        print("\n🚚 2/5 - Criando dim_logistica...")
        con.execute(f"""
            COPY (
                SELECT 
                    ROW_NUMBER() OVER() AS id_logistica,
                    status_entrega,
                    modo_envio,
                    AVG(dias_envio_real) AS dias_envio_real,
                    AVG(dias_envio_agendado) AS dias_envio_agendado
                FROM (
                    SELECT DISTINCT 
                        status_entrega, 
                        modo_envio,
                        dias_envio_real,
                        dias_envio_agendado
                    FROM silver_data
                )
                GROUP BY status_entrega, modo_envio
            ) TO '{OUTPUT_GOLD_DIR}/dim_logistica.parquet' (FORMAT PARQUET)
        """)
        
        log_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_logistica.parquet')").fetchone()[0]
        print(f"   ✅ {log_count} combinações de status/modo criadas")

        # ========================================================================
        # 3. DIMENSÃO PRODUTOS - Categoria + Nome
        # ========================================================================
        print("\n📦 3/5 - Criando dim_produtos...")
        con.execute(f"""
            COPY (
                SELECT 
                    ROW_NUMBER() OVER() AS id_produto,
                    categoria,
                    nome_produto
                FROM (
                    SELECT DISTINCT 
                        categoria,
                        nome_produto
                    FROM silver_data
                    WHERE categoria IS NOT NULL
                )
                ORDER BY categoria, nome_produto
            ) TO '{OUTPUT_GOLD_DIR}/dim_produtos.parquet' (FORMAT PARQUET)
        """)
        
        prod_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_produtos.parquet')").fetchone()[0]
        print(f"   ✅ {prod_count:,} produtos únicos criados")

        # ========================================================================
        # 4. DIMENSÃO CLIENTES - Cidade + Estado + País
        # ========================================================================
        print("\n👤 4/5 - Criando dim_clientes...")
        con.execute(f"""
            COPY (
                SELECT 
                    ROW_NUMBER() OVER() AS id_cliente,
                    cliente_cidade,
                    cliente_estado,
                    cliente_pais
                FROM (
                    SELECT DISTINCT 
                        cliente_cidade,
                        cliente_estado,
                        cliente_pais
                    FROM silver_data
                    WHERE cliente_cidade IS NOT NULL
                )
                ORDER BY cliente_pais, cliente_estado, cliente_cidade
            ) TO '{OUTPUT_GOLD_DIR}/dim_clientes.parquet' (FORMAT PARQUET)
        """)
        
        cli_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_clientes.parquet')").fetchone()[0]
        print(f"   ✅ {cli_count:,} localizações únicas criadas")

        # ========================================================================
        # 5. DIMENSÃO CONTEXTO - Petróleo Brent
        # ========================================================================
        print("\n🛢️ 5/5 - Criando dim_contexto...")
        con.execute(f"""
            COPY (
                SELECT 
                    data_pedido AS data_referencia,
                    AVG(preco_petroleo_brent) AS preco_brent
                FROM silver_data
                GROUP BY data_pedido
            ) TO '{OUTPUT_GOLD_DIR}/dim_contexto.parquet' (FORMAT PARQUET)
        """)
        
        ctx_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_contexto.parquet')").fetchone()[0]
        print(f"   ✅ {ctx_count} valores de Brent únicos")

        # ========================================================================
        # TABELA FATO - Centro do Star Schema
        # ========================================================================
        print("\n💰 Gerando fact_vendas (Centro do Star Schema)...")
        
        con.execute(f"""
            COPY (
                SELECT 
                    s.data_pedido AS id_tempo,
                    s.data_pedido AS data_completa,
                    p.id_produto,
                    c.id_cliente,
                    l.id_logistica,
                    s.preco_petroleo_brent as brent_diario,
                    s.valor_venda,
                    s.lucro_pedido,
                    s.venda_por_cliente,
                    s.dias_envio_real
                FROM silver_data s
                LEFT JOIN (SELECT id_produto, categoria, nome_produto FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_produtos.parquet')) p 
                    ON s.categoria = p.categoria AND s.nome_produto = p.nome_produto
                LEFT JOIN (SELECT id_cliente, cliente_cidade, cliente_estado, cliente_pais FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_clientes.parquet')) c 
                    ON s.cliente_cidade = c.cliente_cidade AND s.cliente_estado = c.cliente_estado
                LEFT JOIN (SELECT id_logistica, status_entrega, modo_envio FROM read_parquet('{OUTPUT_GOLD_DIR}/dim_logistica.parquet')) l 
                    ON s.status_entrega = l.status_entrega AND s.modo_envio = l.modo_envio
            ) TO '{OUTPUT_GOLD_DIR}/fact_vendas.parquet' (FORMAT PARQUET)
        """)
        
        fact_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUTPUT_GOLD_DIR}/fact_vendas.parquet')").fetchone()[0]
        print(f"   ✅ {fact_count:,} transações na tabela fato")

        # ========================================================================
        # VALIDAÇÃO FINAL
        # ========================================================================
        print("\n" + "="*70)
        print("🎉 STAR SCHEMA CRIADO COM SUCESSO!")
        print("="*70)
        
        # Criar arquivo de validação
        validation_path = os.path.join(OUTPUT_GOLD_DIR, "VALIDACAO.txt")
        with open(validation_path, 'w', encoding='utf-8') as f:
            f.write("VALIDAÇÃO DO STAR SCHEMA\n")
            f.write("="*70 + "\n\n")
            f.write(f"📅 dim_tempo: {tempo_count:,} registros\n")
            f.write(f"🚚 dim_logistica: {log_count} registros\n")
            f.write(f"📦 dim_produtos: {prod_count:,} registros\n")
            f.write(f"👤 dim_clientes: {cli_count:,} registros\n")
            f.write(f"🛢️ dim_contexto: {ctx_count} registros\n")
            f.write(f"💰 fact_vendas: {fact_count:,} registros\n\n")
            f.write("✅ Todas as dimensões e fato foram criadas com sucesso!\n")
        
        print(f"\n📋 Resumo:")
        print(f"   • dim_tempo: {tempo_count:,} datas")
        print(f"   • dim_logistica: {log_count} combinações")
        print(f"   • dim_produtos: {prod_count:,} produtos")
        print(f"   • dim_clientes: {cli_count:,} localizações")
        print(f"   • dim_contexto: {ctx_count} valores Brent")
        print(f"   • fact_vendas: {fact_count:,} transações")
        
        print(f"\n📁 Arquivos salvos em: {OUTPUT_GOLD_DIR}/")
        print(f"📄 Validação salva em: {validation_path}")
        
        # Teste rápido de integridade
        print("\n🔍 Teste de Integridade...")
        test_query = con.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(valor_venda) as faturamento_total,
                AVG(lucro_pedido) as lucro_medio
            FROM read_parquet('{OUTPUT_GOLD_DIR}/fact_vendas.parquet')
        """).df()
        
        print(f"   Total de vendas: {test_query['total'].iloc[0]:,}")
        print(f"   Faturamento: ${test_query['faturamento_total'].iloc[0]:,.2f}")
        print(f"   Lucro médio: ${test_query['lucro_medio'].iloc[0]:,.2f}")
        
        print("\n✅ Pipeline Gold concluído! Pronto para o Dashboard.")

    except Exception as e:
        print(f"\n❌ ERRO na camada Gold: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        con.close()

if __name__ == "__main__":
    create_gold_layer_complete()