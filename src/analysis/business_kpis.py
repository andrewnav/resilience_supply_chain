import duckdb

def run_business_analysis():
    con = duckdb.connect()
    print("📊 EXTRAINDO INSIGHTS DA CAMADA GOLD...")

    # SQL que cruza a Fato com as Dimensões (O poder do Star Schema)
    query = """
        SELECT 
            p.categoria,
            COUNT(f.id_produto) as total_pedidos,
            ROUND(SUM(f.valor_venda), 2) as faturamento_total,
            ROUND(AVG(f.preco_petroleo_brent), 2) as media_petroleo_brent,
            ROUND(SUM(f.lucro_pedido), 2) as lucro_total
        FROM read_parquet('data/gold/fact_vendas.parquet') f
        JOIN read_parquet('data/gold/dim_produtos.parquet') p ON f.id_produto = p.id_produto
        GROUP BY p.categoria
        ORDER BY faturamento_total DESC
        LIMIT 5;
    """
    
    result = con.execute(query).df()
    print("\n🏆 TOP 5 CATEGORIAS POR FATURAMENTO:")
    print(result)
    
    # Insight de Logística
    query_log = """
        SELECT 
            l.status_entrega,
            COUNT(*) as total
        FROM read_parquet('data/gold/fact_vendas.parquet') f
        JOIN read_parquet('data/gold/dim_logistica.parquet') l ON f.id_logistica = l.id_logistica
        GROUP BY 1
    """
    print("\n🚚 STATUS DE LOGÍSTICA:")
    print(con.execute(query_log).df())

if __name__ == "__main__":
    run_business_analysis()