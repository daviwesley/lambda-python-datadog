# lambda-python-datadog

> Aplicação web FastAPI executada em **AWS Lambda**, implantada com o [Serverless Framework](https://www.serverless.com/), e totalmente instrumentada com **Datadog** para observabilidade (rastreamentos APM, métricas e logs).

---

## Arquitetura

```
API Gateway HTTP API
       │
       ▼
AWS Lambda  (Python 3.12)
  ├── app/handler.py       ← Ponto de entrada Lambda (Mangum + datadog_lambda_wrapper)
  ├── app/main.py          ← Fábrica de aplicação FastAPI + Datadog TraceMiddleware
  └── app/routes/
        ├── health.py      ← GET /health
        └── items.py       ← CRUD /items
```

**Pilha de observabilidade**

| Sinal  | Ferramenta |
|---------|------|
| Rastreamentos (APM) | `ddtrace` + Datadog Lambda Layer |
| Métricas (Datadog) | Métricas Lambda Aprimoradas via `datadog-lambda` |
| Métricas (CloudWatch) | Powertools `Metrics` via EMF (Embedded Metrics Format) |
| Logs | Powertools `Logger` (JSON estruturado) correlacionado com rastreamentos via `DD_LOGS_INJECTION=true` |

---

## Pré-requisitos

| Ferramenta | Versão | Notas |
|------|---------|-------|
| Python | 3.12 | `brew install python@3.12` no macOS |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 | `brew install uv` no macOS |
| Node.js | ≥ 18 | `brew install node` no macOS |
| Serverless Framework | 3.x | instalado via `npm install` |
| AWS CLI | qualquer | necessário apenas para implantação |
| Docker Desktop | qualquer | necessário apenas para implantação no macOS |

---

## Início rápido

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/daviwesley/lambda-python-datadog.git
cd lambda-python-datadog

# Cria .venv e instala dependências de runtime + desenvolvimento via uv
make install

# Plugins do Serverless Framework
npm install
```

### 2. Executar localmente

```bash
make run
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

`DD_TRACE_ENABLED` é definido como `false` para execuções locais, portanto, o ddtrace não tenta alcançar um Agente Datadog.

### 3. Executar testes

```bash
make test
```

---

## Desenvolvimento local no macOS

Sim — a aplicação executa totalmente no macOS sem qualquer conta AWS ou Agente Datadog.

### Pré-requisitos

Instale as ferramentas necessárias com o [Homebrew](https://brew.sh):

```bash
# Python 3.12
brew install python@3.12

# uv (gerenciador de pacotes Python rápido)
brew install uv
# alternativamente, o instalador oficial também funciona no macOS:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js (para Serverless Framework e plugins)
brew install node
```

> **Docker Desktop** é necessário apenas quando você quer fazer implantação no macOS.
> `serverless-python-requirements` executa um container `lambci/lambda:build-python3.12`
> automaticamente para produzir wheels compatíveis com Linux (por exemplo, `ddtrace`).
> Para `make run` e `make test`, Docker **não** é necessário.

### Executar o servidor localmente

```bash
make install   # cria .venv e instala todas as dependências
make run       # → http://localhost:8000
               # → http://localhost:8000/docs  (Swagger UI)
```

`DD_TRACE_ENABLED=false` é definido automaticamente, portanto, o ddtrace nunca tenta se conectar a um Agente Datadog. A API funciona de forma idêntica à produção — apenas os sinais de observabilidade (rastreamentos, métricas) são suprimidos.

### Executar os testes

```bash
make test
```

Todos os testes são executados em processo, sem necessidade de serviços externos.

### Implantar no macOS

O Docker Desktop deve estar em execução antes de você fazer a implantação:

```bash
# Inicie o Docker Desktop e depois:
make deploy
```

`serverless-python-requirements` executará um container `lambci/lambda:build-python3.12`
automaticamente para produzir wheels compatíveis com Linux.

---

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|----------|-------------|
| `DD_API_KEY` | ✅ | Chave de API Datadog bruta (definida como variável do GitHub Actions — veja a seção CI/CD) |
| `DD_SITE` | ✅ | Site Datadog, por exemplo, `datadoghq.com` ou `datadoghq.eu` |
| `APP_VERSION` | opcional | Tag de versão semântica injetada como `DD_VERSION` (padrão: `1.0.0`) |

Exporte as variáveis para uma implantação manual:

```bash
export DD_API_KEY="YOUR_DD_API_KEY"
export DD_SITE="datadoghq.com"
```

### Implantar em `dev`

```bash
make deploy
# ou
npx serverless deploy --stage dev
```

### Implantar em `prod`

```bash
make deploy-prod
# ou
npx serverless deploy --stage prod
```

### Remover uma pilha

```bash
make remove STAGE=dev
```

---

## CI/CD (GitHub Actions)

Dois fluxos de trabalho estão inclusos em `.github/workflows/`:

| Fluxo de trabalho | Arquivo | Acionador |
|----------|------|---------|
| **CI** | `ci.yml` | A cada push e pull request |
| **Deploy** | `deploy.yml` | Push em `main` → `dev`; tag `v*` → `prod` |

### Segredos necessários do GitHub

Navegue até **Settings → Secrets and variables → Actions → Secrets** em seu repositório e adicione:

| Segredo | Descrição |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | Chave de acesso do AWS IAM com permissões de implantação Lambda / CloudFormation |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta correspondente do AWS IAM |

### Variáveis necessárias do GitHub

Navegue até **Settings → Secrets and variables → Actions → Variables** e adicione:

| Variável | Descrição | Padrão |
|----------|-------------|---------|
| `DD_API_KEY` | Chave de API Datadog bruta usada no momento da implantação | _(nenhuma — deve ser definida)_ |
| `DD_SITE` | Site de ingestão Datadog (por exemplo, `datadoghq.com`) | _(nenhuma — deve ser definida)_ |
| `AWS_REGION` | Região AWS para implantar | `us-east-1` |

### Fluxo de implantação

```
push em main  ─────────────────► implantar em dev  (APP_VERSION = git SHA)
push tag v1.2.3  ──────────────► implantar em prod (APP_VERSION = v1.2.3)
```

Os trabalhos `dev` e `prod` usam [Ambientes](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) do GitHub, portanto, você pode adicionar regras de proteção de implantação (por exemplo, exigir aprovação manual antes de prod).

### Permissões IAM mínimas

O usuário do IAM referenciado pelos segredos AWS precisa das seguintes permissões para fazer a implantação:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "lambda:*",
        "apigateway:*",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PassRole",
        "logs:DescribeLogGroups",
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Referência de API

| Método | Caminho | Descrição |
|--------|------|-------------|
| `GET` | `/health` | Verificação de saúde |
| `GET` | `/items` | Listar todos os itens |
| `POST` | `/items` | Criar um item |
| `GET` | `/items/{id}` | Obter um item por ID |
| `DELETE` | `/items/{id}` | Deletar um item |

Documentação interativa disponível em `/docs` (Swagger UI) e `/redoc`.

---

## Estrutura do projeto

```
.
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint + test a cada push/PR
│       └── deploy.yml          # Implantar em dev (main) / prod (tags v*)
├── app/
│   ├── __init__.py
│   ├── handler.py          # Ponto de entrada Lambda
│   ├── main.py             # Fábrica de aplicação FastAPI
│   ├── powertools.py       # Singletons compartilhados de Logger e Metrics
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       └── items.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── .python-version         # Fixa Python 3.12 para uv
├── pyproject.toml          # Fonte única da verdade para todas as dependências
├── uv.lock                 # Arquivo de bloqueio de dependência completo (comprometido)
├── requirements.txt        # Auto-gerado por `make export-requirements` para empacotamento Lambda
├── serverless.yml          # IaC do Serverless Framework
├── package.json            # Plugins do Serverless
├── pytest.ini              # Configuração de teste
├── Makefile
└── README.md
```

> **`requirements.txt` é auto-gerado** por `uv export` e não deve ser editado manualmente.  
> Execute `make export-requirements` após alterar dependências em `pyproject.toml`.

---

## AWS Lambda Powertools

[AWS Lambda Powertools para Python](https://docs.powertools.aws.dev/lambda/python/latest/) é integrado via `app/powertools.py`, que expõe dois singletons compartilhados importados em toda a aplicação.

Rastreamento é tratado exclusivamente por **Datadog APM** (`ddtrace` + `TraceMiddleware`). O Powertools Tracer / AWS X-Ray não é usado.

### Logger

O `Logger` do Powertools substitui o logging stdlib e produz JSON estruturado em cada invocação:

```json
{
  "level": "INFO",
  "location": "list_items:app/routes/items.py:23",
  "message": "Listando itens",
  "item_count": 3,
  "service": "lambda-python-datadog",
  "cold_start": true,
  "function_name": "lambda-python-datadog-dev-api",
  "correlation_id": "abc-123"
}
```

O decorador `@logger.inject_lambda_context` no manipulador adiciona automaticamente `cold_start`, `function_name`, `function_arn` e `request_id` a cada linha de log.  
O middleware de ID de correlação do FastAPI em `app/main.py` encaminha o cabeçalho `x-amzn-requestid` do API Gateway, portanto, todos os logs dentro de uma solicitação compartilham o mesmo `correlation_id`.

### Variáveis de ambiente (definidas em `serverless.yml`)

| Variável | Valor | Finalidade |
|----------|-------|---------|
| `POWERTOOLS_SERVICE_NAME` | `lambda-python-datadog` | Marca cada log/métrica |
| `POWERTOOLS_LOG_LEVEL` | `INFO` | Nível mínimo de log |
| `POWERTOOLS_METRICS_NAMESPACE` | `LambdaPythonDatadog` | Namespace CloudWatch |

---

## Detalhes de configuração do Datadog

O plugin `serverless-plugin-datadog` faz automaticamente:

1. Anexa a **Camada Datadog Lambda** (contém o Datadog Forwarder & ddtrace).
2. Define todas as variáveis de ambiente necessárias (`DD_API_KEY`, `DD_SITE`, etc.).
3. Ativa as **Métricas Lambda Aprimoradas** (invocações faturadas, erros, inicializações frias, etc.).
4. Ativa a **Correlação de logs** — cada linha de log é marcada com o `trace_id` / `span_id` ativo.

O `TraceMiddleware` em `app/main.py` cria um span APM Datadog para cada solicitação HTTP, visível em **APM > Services** na interface do Datadog.

### Marcação de Serviço Unificada

As seguintes tags são definidas automaticamente em `serverless.yml`:

| Tag | Valor |
|-----|-------|
| `service` | `lambda-python-datadog` |
| `env` | Estágio Serverless (`dev`, `prod`, …) |
| `version` | Variável de ambiente `APP_VERSION` |

---

## Custos da Infraestrutura

Esta aplicação aproveita o **AWS Free Tier** e da camada gratuita de diversos serviços. Abaixo estão os principais custos:

### API Gateway (HTTP API)
- **$1/million requests** (após os primeiros 300 milhões inclusos no Free Tier)

### AWS CloudWatch
- **PutLogEvents**: Primeiros 5GB/mês de dados de logs ingeridos são gratuitos
- **StartQuery**: Primeiros 5GB/mês de dados de logs escaneados por CloudWatch Logs Insights são gratuitos
- **Storage (ByteHrs)**: Primeiros 5GB-mês de armazenamento de logs são gratuitos

### AWS Lambda
- **Free Tier**: 1,000,000 de requisições/mês (US East)
- Após atingir o limite: $0.20 por 1 milhão de requisições

### AWS X-Ray
- **Free Tier**: 1,000,000 de traces/mês (US East)
- Após atingir o limite: $5.00 por 1 milhão de traces adicionais

> Para aplicações com baixo/médio tráfego, a maioria dos custos permanecerá dentro do Free Tier.

---

## Licença

[MIT](LICENSE)
