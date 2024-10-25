# PrivacyPoint Site - API do Chat

## Configuração de Ambiente

### Pré-requisitos

- Python 3.10 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes e ambientes
  virtuais)
- [Azure Functions Core Tools](https://docs.microsoft.com/pt-br/azure/azure-functions/functions-run-local?tabs=v4%2Cwindows%2Ccsharp%2Cportal%2Cbash)
- Uma conta na OpenAI com acesso à API

### Configuração do Ambiente com `uv`

1. Clone o repositório:
   ```
   git clone https://github.com/hellmrf/privacy-chat-function
   cd privacy-chat-function
   ```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (ou
   configure as variáveis de ambiente):
   ```
   OPENAI_API_KEY=sua_chave_api_da_openai
   OPENAI_ASSISTANT_ID=id_do_seu_assistente_openai
   ```

3. Execute a função localmente para testes:
   ```
   uv run func start
   ```

## Executando Localmente

Para executar a função localmente:

1. Execute o comando:
   ```
   uv run func start
   ```

## Estrutura do Projeto

- `function_app.py`: Contém as definições das rotas de API.
- `src/api.py`: Implementa a lógica principal de interação com a API da OpenAI.
- `src/defs/`: Contém definições de tipos, erros e respostas.

## Desenvolvimento

Para desenvolvimento, recomenda-se usar o Visual Studio Code com as extensões
Azure Functions e Python.
