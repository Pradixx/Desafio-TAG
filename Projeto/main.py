from Projeto.src.dados import carregar_planilha, validar_dados
from Projeto.src.analise import classificar_perfil, gerar_alerta, gerar_resumo_ia
from Projeto.src.relatorio import gerar_relatorio, salvar_relatorio, enviar_email

# Caminhos dos arquivos
CAMINHO_PLANILHA = "data/clientes_TAG.xlsx"
CAMINHO_RELATORIO = "output/relatorio.json"


def main():
    print("=" * 50)
    print("  TAG Investimentos — Análise de Carteira")
    print("=" * 50)

    # --- Etapa 1: Carrega e valida a planilha ---
    df, avisos = validar_dados(carregar_planilha(CAMINHO_PLANILHA))

    if avisos:
        print(f"\nAvisos de qualidade de dados encontrados em {len(avisos)} cliente(s):")
        for nome, lista in avisos.items():
            for aviso in lista:
                print(f"  [{nome}] {aviso}")

    # --- Etapa 2: Analisa cada cliente ---
    print(f"\nIniciando análise de {len(df)} clientes...\n")
    resultados = []

    for i, row in df.iterrows():
        cliente = row.to_dict()
        nome = cliente["nome"]
        print(f"  Processando {i + 1}/{len(df)} — {nome}...")

        # Classifica o perfil e verifica alertas
        perfil = classificar_perfil(cliente)
        alerta = gerar_alerta(cliente, perfil)
        avisos_cliente = avisos.get(nome, [])

        # Chama a IA para gerar o resumo em linguagem natural
        resumo = gerar_resumo_ia(cliente, perfil, alerta, avisos_cliente)

        resultados.append({
            "nome": nome,
            "perfil_risco": perfil,
            "resumo": resumo,
            "alerta": alerta,
            "avisos_qualidade_dados": avisos_cliente,
        })

    # --- Etapa 3: Gera e salva o relatório ---
    print("\nGerando relatório...")
    relatorio = gerar_relatorio(resultados)
    salvar_relatorio(relatorio, CAMINHO_RELATORIO)

    # --- Etapa 4: Envia por e-mail ---
    print("Enviando relatório por e-mail...")
    enviar_email(CAMINHO_RELATORIO)

    # --- Resumo final ---
    print("\n" + "=" * 50)
    print(f"  Concluído! {relatorio['total_clientes']} clientes analisados.")
    print(f"  Alertas encontrados: {relatorio['total_alertas']}")
    print(f"  Relatório salvo em: {CAMINHO_RELATORIO}")
    print("=" * 50)


if __name__ == "__main__":
    main()
