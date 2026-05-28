# TAG Investimentos — Desafio Técnico

Script Python que lê uma planilha de clientes, analisa o perfil de risco de cada um usando IA e gera um relatório automatizado.

---

## Estrutura do projeto

```
Desafio_TAG/
├── src/
│   ├── dados.py           # leitura e validação da planilha
│   ├── analise.py         # classificação de risco e chamada à IA
│   └── relatorio.py       # geração do JSON e envio por e-mail
├── data/                  # coloque a planilha aqui (não sobe no git)
├── output/                # relatório gerado (não sobe no git)
├── main.py                # script principal
├── .env.example           # template das variáveis de ambiente
├── requirements.txt
└── README.md
```

---

## Como rodar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.example .env
```

Abra o `.env` e preencha:

```
GEMINI_API_KEY=sua_chave_aqui       # obtenha em: aistudio.google.com
GROQ_API_KEY=sua_chave_aqui         # fallback — obtenha em: console.groq.com
EMAIL_FROM=seu_email@gmail.com
EMAIL_TO=destinatario@gmail.com
EMAIL_PASSWORD=senha_de_app_gmail   # gere em: myaccount.google.com/apppasswords
```

> Para o Gmail, use uma **Senha de App** (não a senha normal da conta).

### 3. Coloque a planilha na pasta correta

```
data/clientes_TAG.xlsx
```

### 4. Execute

```bash
python main.py
```

O relatório será salvo em `output/relatorio.json` e enviado por e-mail.

---

## Formato do relatório gerado

```json
{
  "gerado_em": "27/05/2026 14:30",
  "total_clientes": 20,
  "total_alertas": 4,
  "clientes": [
    {
      "nome": "Ana Luiza Ferreira",
      "perfil_risco": "conservador",
      "resumo": "Ana Luiza, 62 anos...",
      "alerta": null,
      "avisos_qualidade_dados": []
    }
  ]
}
```

---

## Decisões técnicas

### Classificação de perfil de risco

O perfil é calculado com base na soma de `perc_renda_variavel + perc_cripto`, que representa a exposição total a ativos de risco:

| Exposição ao risco | Perfil       |
|--------------------|--------------|
| Menor que 20%      | Conservador  |
| Entre 20% e 50%    | Moderado     |
| Acima de 50%       | Arrojado     |

A detecção de alerta compara o perfil calculado com o objetivo declarado:
- `preservacao` → espera conservador
- `aposentadoria` → espera conservador ou moderado
- `crescimento` → espera moderado ou arrojado

### Tratamento de inconsistências da planilha

A planilha foi entregue com dados propositalmente inconsistentes. Abaixo estão os casos identificados e como cada um foi tratado:

| Cliente | Problema | Tratamento |
|---------|----------|------------|
| Eduardo Fontes | `idade` nula | Mantido como nulo; análise de perfil fica parcial; registrado nos avisos |
| Thiago Azevedo | `patrimonio_total` nulo | Mantido como nulo; não usado na lógica de risco; registrado nos avisos |
| Isabela Prado | `perc_cripto` nulo | Calculado como `100 - variavel - fixa = 5%`; registrado nos avisos |
| Sônia Brandão | 69 anos, objetivo `aposentadoria`, mas 75% variável + 10% cripto | Perfil calculado como arrojado → alerta gerado |
| Fernanda Queiroz | 60 anos, objetivo `preservacao`, mas 80% em cripto | Perfil calculado como arrojado → alerta gerado |
| Carlos Uchoa | 45 anos, objetivo `aposentadoria`, mas 90% variável | Perfil calculado como arrojado → alerta gerado |
| Lucas Evangelista | 27 anos, objetivo `crescimento`, mas 5% variável e 90% renda fixa | Perfil calculado como conservador → alerta gerado |

### API de IA

O script tenta o **Gemini** primeiro. Se a chamada falhar (chave inválida, rate limit, etc.), tenta o **Groq** como fallback. Se ambos falharem, o resumo é substituído por uma mensagem informativa e a execução continua normalmente.

### Segurança

- Chaves de API ficam exclusivamente no arquivo `.env`, que está no `.gitignore`
- A planilha de clientes e os relatórios gerados também estão no `.gitignore`
