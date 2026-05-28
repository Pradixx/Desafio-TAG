import json
import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def gerar_relatorio(resultados: list) -> dict:
    """Monta o dicionário final com o resumo de todos os clientes analisados."""
    alertas = [r for r in resultados if r["alerta"]]

    return {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_clientes": len(resultados),
        "total_alertas": len(alertas),
        "clientes": resultados,
    }


def salvar_relatorio(relatorio: dict, caminho: str) -> None:
    """Salva o relatório em formato JSON com indentação legível."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"Relatório salvo em: {caminho}")


def enviar_email(caminho_relatorio: str) -> None:
    """
    Envia o relatório JSON como anexo de e-mail.
    As credenciais são lidas do arquivo .env.
    """
    # Lê as configurações do .env
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    email_password = os.getenv("EMAIL_PASSWORD")

    # Valida se as variáveis obrigatórias foram configuradas
    if not all([email_from, email_to, email_password]):
        print("E-mail não enviado: configure EMAIL_FROM, EMAIL_TO e EMAIL_PASSWORD no .env")
        return

    # Lê o relatório para montar o corpo do e-mail
    with open(caminho_relatorio, "r", encoding="utf-8") as f:
        relatorio = json.load(f)

    corpo = (
        f"Olá,\n\n"
        f"Segue em anexo o relatório de análise de carteira gerado em {relatorio['gerado_em']}.\n\n"
        f"Total de clientes analisados: {relatorio['total_clientes']}\n"
        f"Total de alertas encontrados: {relatorio['total_alertas']}\n\n"
        f"Atenciosamente,\nSistema de Análise TAG"
    )

    # Monta o e-mail
    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = "[TAG] Relatório de Análise de Carteira"
    msg.attach(MIMEText(corpo, "plain"))

    # Adiciona o arquivo JSON como anexo
    with open(caminho_relatorio, "rb") as f:
        anexo = MIMEBase("application", "octet-stream")
        anexo.set_payload(f.read())

    encoders.encode_base64(anexo)
    anexo.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(caminho_relatorio)}",
    )
    msg.attach(anexo)

    # Envia via SMTP
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as servidor:
            servidor.starttls()  # criptografa a conexão
            servidor.login(email_from, email_password)
            servidor.sendmail(email_from, email_to, msg.as_string())
        print(f"E-mail enviado para: {email_to}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
