import pandas as pd

TARIFA_BOLETO = 4.58

# 1. Ler o arquivo CSV
df = pd.read_csv("extrato5.csv", sep=",", encoding="utf-8")

# 2. Padronizar os nomes das colunas
df.columns = df.columns.str.strip().str.lower()
if "unidade" in df.columns:
    df = df.rename(columns={"unidade": "modulo"})

# 3. Converter a coluna de pagamento para data real
df["pagamento"] = pd.to_datetime(df["pagamento"], dayfirst=True, errors="coerce")

# 4. Tratar valor numérico (remove ponto de milhar e troca vírgula por ponto)
df["liquidado"] = (
    df["liquidado"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# 5. Identificar taxa
coluna_busca = "prestacao" if "prestacao" in df.columns else "modulo"
df["tem_taxa_boleto"] = df[coluna_busca].astype(str).str.lower().str.contains("presta", na=False)

# 6. Calcular taxa e valor líquido de entrada
df["taxa"] = df["tem_taxa_boleto"].apply(lambda x: TARIFA_BOLETO if x else 0.0)
df["valor_entrada"] = df["liquidado"] - df["taxa"]

# 7. Ordenar por data (e desempatar por módulo no mesmo dia)
df = df.sort_values(by=["pagamento", "modulo"], ascending=[True, True])

# 8. Agrupar por data de pagamento (já sai ordenado cronologicamente)
agrupado = df.groupby("pagamento")["valor_entrada"].sum().reset_index()

# 9. Formatar datas e valores para exibição
df["pagamento_fmt"] = df["pagamento"].dt.strftime("%d/%m/%Y")
agrupado["Data"] = agrupado["pagamento"].dt.strftime("%d/%m/%Y")
agrupado["Valor Entrada"] = agrupado["valor_entrada"].map("R$ {:.2f}".format)

# 10. Saída única e limpa no terminal
print("Detalhamento das linhas:")
print(df[["pagamento_fmt", "modulo", "liquidado", "taxa", "valor_entrada"]].to_string(index=False))

print("\nResumo por data (com taxas descontadas):")
print(agrupado[["Data", "Valor Entrada"]].to_string(index=False))

# --- ADICIONE ISSO NO FINAL DO SEU SCRIPT ---

# Transformar as duas tabelas em HTML
tabela_resumo_html = agrupado[["Data", "Valor Entrada"]].to_html(index=False)
tabela_detalhe_html = df[["pagamento_fmt", "modulo", "liquidado", "taxa", "valor_entrada"]].to_html(index=False)

# Montar a estrutura da página com um visual básico (CSS) para ficar legível
conteudo_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Conciliação</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 700px; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f4f6f8; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}
    </style>
</head>
<body>
    <h2>Resumo por Data (Com Taxas Descontadas)</h2>
    {tabela_resumo_html}

    <h2>Detalhamento das Linhas</h2>
    {tabela_detalhe_html}
</body>
</html>
"""

# Salvar o arquivo HTML
with open("relatorio_conciliacao.html", "w", encoding="utf-8") as f:
    f.write(conteudo_html)

print("\nRelatório gerado com sucesso: relatorio_conciliacao.html")