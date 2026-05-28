import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def classificar_perfil(cliente: dict) -> str:
    """
    Classifica o perfil de risco do cliente com base nos percentuais de alocação.
    A soma de renda variável + cripto representa o grau de exposição a risco.
    """
    exposicao_risco = cliente["perc_renda_variavel"] + cliente["perc_cripto"]

    if exposicao_risco < 20:
        return "conservador"
    elif exposicao_risco <= 50:
        return "moderado"
    else:
        return "arrojado"


def gerar_alerta(cliente: dict, perfil: str) -> str | None:
    """
    Compara o perfil calculado com o objetivo declarado pelo cliente.
    Retorna um texto de alerta se houver inconsistência, ou None se estiver ok.
    """
    objetivo = cliente["objetivo"]

    # Mapa de compatibilidade: para cada objetivo, quais perfis são esperados
    perfis_esperados = {
        "preservacao": ["conservador"],
        "aposentadoria": ["conservador", "moderado"],
        "crescimento": ["moderado", "arrojado"],
    }

    esperados = perfis_esperados.get(objetivo, [])

    if perfil not in esperados:
        return (
            f"ALERTA: perfil calculado é '{perfil}', mas o objetivo declarado é "
            f"'{objetivo}' (esperado: {' ou '.join(esperados)}). "
            f"Revisar alocação com o cliente."
        )

    return None


def _montar_prompt(cliente: dict, perfil: str, alerta: str | None, avisos: list) -> str:
    """Monta o texto do prompt enviado à IA com todos os dados do cliente."""
    linhas = [
        "Você é um analista de investimentos da TAG Investimentos.",
        "Escreva um parágrafo curto (3 a 5 frases) em português sobre o perfil do cliente abaixo.",
        "Use linguagem profissional e direta. Mencione o alerta, se houver.",
        "",
        f"Nome: {cliente['nome']}",
        f"Idade: {cliente['idade'] if cliente['idade'] else 'não informada'}",
        f"Patrimônio total: R$ {cliente['patrimonio_total']:,.0f}" if cliente["patrimonio_total"] else "Patrimônio total: não informado",
        f"Renda variável: {cliente['perc_renda_variavel']}%",
        f"Renda fixa: {cliente['perc_renda_fixa']}%",
        f"Cripto: {cliente['perc_cripto']:.0f}%",
        f"Objetivo: {cliente['objetivo']}",
        f"Perfil de risco calculado: {perfil}",
    ]

    if alerta:
        linhas.append(f"Alerta: {alerta}")

    if avisos:
        linhas.append(f"Observações sobre os dados: {'; '.join(avisos)}")

    return "\n".join(linhas)


def gerar_resumo_ia(cliente: dict, perfil: str, alerta: str | None, avisos: list) -> str:
    """
    Envia os dados do cliente para a IA e retorna o resumo gerado.
    Tenta o Groq primeiro; se falhar, tenta o Gemini como fallback.
    """
    prompt = _montar_prompt(cliente, perfil, alerta, avisos)

    # --- Tentativa 1: Groq ---
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            cliente_groq = Groq(api_key=groq_key)
            resposta = cliente_groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
            )
            return resposta.choices[0].message.content.strip()
        except Exception as e:
            print(f"  Groq falhou para {cliente['nome']}: {e}. Tentando Gemini...")

    # --- Tentativa 2: Gemini (fallback) ---
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            modelo = genai.GenerativeModel("gemini-2.0-flash-lite")
            resposta = modelo.generate_content(prompt)
            return resposta.text.strip()
        except Exception as e:
            print(f"  Gemini também falhou para {cliente['nome']}: {e}")

    # --- Fallback final: sem IA disponível ---
    return "[Resumo indisponível: nenhuma API de IA configurada ou ambas falharam]"
