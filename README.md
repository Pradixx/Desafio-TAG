# TAG Investimentos - Desafio Técnico

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
GROQ_API_KEY=sua_chave_aqui         # fallback - obtenha em: console.groq.com
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

### Separação do código em módulos

A primeira decisão foi não colocar tudo em um único arquivo. Separei o código em três módulos com responsabilidades distintas (`dados.py`, `analise.py`, `relatorio.py`) orquestrados pelo `main.py`. Isso facilita a manutenção - se a API de IA mudar, só altero `analise.py`. Se o formato do relatório mudar, só altero `relatorio.py`. Cada parte pode ser testada e entendida de forma independente.

---

### Classificação de perfil de risco

A métrica escolhida foi a **soma de `perc_renda_variavel + perc_cripto`**, que representa a exposição total do cliente a ativos de alto risco. Renda fixa foi excluída do cálculo por ser o componente de menor volatilidade.

| Exposição ao risco | Perfil       | Raciocínio |
|--------------------|--------------|------------|
| Menor que 20%      | Conservador  | Carteira predominantemente em renda fixa, baixa tolerância a risco |
| Entre 20% e 50%    | Moderado     | Equilíbrio entre segurança e crescimento |
| Acima de 50%       | Arrojado     | Mais da metade da carteira em ativos voláteis |

A detecção de alerta compara o perfil calculado com o objetivo declarado pelo cliente:

| Objetivo declarado | Perfis compatíveis | Lógica |
|---|---|---|
| `preservacao` | conservador | Quem quer preservar patrimônio não deve ter exposição relevante a risco |
| `aposentadoria` | conservador ou moderado | Tolerância moderada dependendo da idade, mas sem concentração em ativos voláteis |
| `crescimento` | moderado ou arrojado | Quem busca crescimento precisa de alguma exposição a risco |

Se o perfil calculado não estiver entre os compatíveis com o objetivo, um alerta é gerado e incluído no relatório e no resumo da IA.

---

### Tratamento de inconsistências da planilha

Antes de qualquer processamento, todos os dados passam pela função `validar_dados()`. A premissa adotada foi: **nunca ignorar silenciosamente um problema** - cada inconsistência é tratada de forma explícita e registrada no campo `avisos_qualidade_dados` do relatório.

| Cliente | Problema identificado | Decisão tomada | Justificativa |
|---|---|---|---|
| Isabela Prado | `perc_cripto` nulo | Calculado como `100 - variavel - fixa = 5%` | Os outros percentuais eram válidos; a diferença é a estimativa mais conservadora possível |
| Thiago Azevedo | `patrimonio_total` nulo | Mantido como nulo | Patrimônio não é usado na lógica de classificação de risco - não há como imputar sem distorcer |
| Eduardo Fontes | `idade` nula | Mantido como nulo | Idade influencia o contexto mas não é determinante nas regras de classificação atuais; registrado para que o analista tenha ciência |
| Sônia Brandão | 69 anos, `aposentadoria`, mas 75% variável + 10% cripto | Alerta gerado | Perfil calculado é arrojado - incompatível com o objetivo declarado |
| Fernanda Queiroz | 60 anos, `preservacao`, mas 80% em cripto | Alerta gerado | Caso mais extremo da planilha - 80% em cripto é o oposto de preservação de patrimônio |
| Carlos Uchoa | 45 anos, `aposentadoria`, mas 90% variável | Alerta gerado | Alta concentração em renda variável inconsistente com objetivo de aposentadoria |
| Lucas Evangelista | 27 anos, `crescimento`, mas 5% variável e 90% renda fixa | Alerta gerado | Jovem com objetivo de crescimento mas carteira extremamente conservadora |

---

### Integração com IA

**Por que usar IA para o resumo?**
As regras determinísticas classificam o perfil, mas não produzem texto natural. A IA foi usada especificamente para transformar os dados estruturados em um parágrafo compreensível para um gestor - sem substituir a lógica de negócio, que permanece no código Python.

**Por que separar a lógica de classificação da IA?**
Deliberadamente mantive a classificação (`conservador/moderado/arrojado`) e os alertas no código Python, e não delegado para a IA. Isso garante resultados determinísticos e auditáveis - a IA pode "inventar" ou variar, o código Python não.

**Prompt engineering:**
O prompt enviado à IA inclui todos os dados do cliente, o perfil já calculado, o alerta (se houver) e os avisos de qualidade dos dados. Ao informar o perfil calculado no prompt, a IA não precisa reclassificar - ela foca em redigir o resumo com base em informações já processadas.

**Resiliência com fallback:**
O script tenta o **Groq** primeiro. Se a chamada falhar por qualquer motivo (chave inválida, rate limit, modelo indisponível), tenta o **Gemini**. Se ambos falharem, o resumo recebe uma mensagem informativa e a execução **continua normalmente** para os demais clientes - um erro em um cliente não interrompe o processamento dos outros 19.

**Pausa entre chamadas:**
Foi adicionada uma pausa de 4 segundos entre cada chamada à API (`time.sleep(4)`) para respeitar o limite de tokens por minuto do free tier. Com 20 clientes, o processamento completo leva cerca de 80 segundos.

---

### Formato do relatório

Optei por **JSON** em vez de `.txt` por três motivos:
1. É estruturado - pode ser consumido por outros sistemas futuramente
2. Facilita a leitura programática (filtrar só os alertas, por exemplo)
3. Preserva os tipos de dados (null para ausência de alerta, lista para avisos)

---

### Segurança

- Chaves de API ficam exclusivamente no arquivo `.env`, que está no `.gitignore`
- O `.env.example` documenta quais variáveis são necessárias sem expor valores reais
- A planilha de clientes (`data/`) e os relatórios gerados (`output/`) também estão no `.gitignore` - dados de clientes nunca sobem para o repositório
