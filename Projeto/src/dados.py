import pandas as pd

# Colunas que o script espera encontrar na planilha
COLUNAS_ESPERADAS = [
    "nome",
    "idade",
    "patrimonio_total",
    "perc_renda_variavel",
    "perc_renda_fixa",
    "perc_cripto",
    "objetivo",
]


def carregar_planilha(caminho: str) -> pd.DataFrame:
    """Lê o arquivo .xlsx e retorna um DataFrame. Aborta se o arquivo não existir."""
    try:
        df = pd.read_excel(caminho)
        print(f"Planilha carregada: {len(df)} clientes encontrados.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    except Exception as e:
        raise RuntimeError(f"Erro ao ler a planilha: {e}")


def validar_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Verifica e corrige problemas nos dados de cada cliente.
    Retorna o DataFrame tratado e um dicionário de avisos por cliente.
    """
    # Verifica se todas as colunas esperadas estão presentes
    colunas_faltando = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    if colunas_faltando:
        raise ValueError(f"Colunas faltando na planilha: {colunas_faltando}")

    # Cópia para não alterar o DataFrame original
    df = df.copy()

    # Dicionário para guardar os avisos de qualidade de cada cliente
    avisos = {}

    for i, row in df.iterrows():
        nome = row["nome"]
        avisos_cliente = []

        # --- Tratamento de perc_cripto nulo ---
        # Se cripto está vazio, calcula como o que sobrou dos outros dois percentuais
        if pd.isna(row["perc_cripto"]):
            valor_calculado = 100 - row["perc_renda_variavel"] - row["perc_renda_fixa"]
            df.at[i, "perc_cripto"] = max(valor_calculado, 0)  # nunca negativo
            avisos_cliente.append(
                f"perc_cripto estava nulo — imputado como {df.at[i, 'perc_cripto']:.0f}%"
            )

        # --- Tratamento de idade nula ---
        if pd.isna(row["idade"]):
            avisos_cliente.append("idade não informada — análise de perfil será parcial")

        # --- Tratamento de patrimônio nulo ---
        if pd.isna(row["patrimonio_total"]):
            avisos_cliente.append("patrimônio total não informado")

        # --- Verifica se os percentuais somam 100% ---
        soma = row["perc_renda_variavel"] + row["perc_renda_fixa"] + df.at[i, "perc_cripto"]
        if abs(soma - 100) > 1:  # tolerância de 1% para arredondamentos
            avisos_cliente.append(
                f"percentuais somam {soma:.0f}% (esperado: 100%)"
            )

        if avisos_cliente:
            avisos[nome] = avisos_cliente

    return df, avisos