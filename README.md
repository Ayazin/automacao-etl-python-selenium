# Automação de Coleta e Consolidação de Dados com Python

Projeto demonstrativo de automação de extração, validação e consolidação de dados de tabelas web utilizando Python, Selenium e Pandas.

## Sobre o projeto

O objetivo deste projeto é demonstrar como automatizar tarefas de coleta de dados em aplicações web, reduzir etapas manuais de extração e preparar informações estruturadas para utilização em processos analíticos.

A solução automatiza a navegação pela aplicação de origem, extrai informações de contratos e medições, aplica regras de validação e consolida os dados em arquivos CSV.

**Este repositório contém uma versão demonstrativa, sem credenciais ou dados reais confidenciais.**

## Objetivos

* Automatizar a navegação e a coleta de dados em páginas web.
* Extrair informações estruturadas de tabelas HTML.
* Aplicar regras de validação de negócio durante o processamento.
* Consolidar diferentes tabelas utilizando Pandas.
* Exportar datasets em CSV para utilização em processos de análise de dados e Business Intelligence.

## Tecnologias utilizadas

* **Python:** linguagem principal do projeto.
* **Selenium:** automação de navegador e interação com elementos HTML.
* **Pandas:** transformação, tratamento e consolidação dos dados.
* **WebDriverWait:** sincronização da automação com o carregamento dos elementos da página.
* **CSV:** formato de saída para integração com outras ferramentas analíticas.

## Como funciona

1. **Acesso à aplicação:** abre o navegador e acessa o sistema de origem utilizando credenciais configuradas localmente.
2. **Identificação dos contratos:** percorre os registros disponíveis e coleta informações de identificação.
3. **Extração das tabelas:** coleta os dados de medições e as informações relacionadas.
4. **Validação:** verifica regras de negócio relacionadas ao status e à identificação de medições finais.
5. **Tratamento e consolidação:** utiliza DataFrames do Pandas para normalizar as informações e relacionar os registros pela identificação da medição.
6. **Exportação:** gera arquivos CSV estruturados para utilização em etapas posteriores de análise.

## Resultados gerados

A automação pode produzir dois conjuntos de dados:

* **Informações dos contratos:** dados de identificação e informações gerais extraídas do sistema.
* **Medições consolidadas:** registros de medições reunidos em uma estrutura tabular, com as informações complementares disponíveis.

Os arquivos de demonstração, quando disponibilizados, utilizam dados fictícios e não representam registros reais do sistema de origem.

## Estrutura do projeto

```text
automacao-etl-python-selenium/
├── README.md
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── docs/
└── samples/
```

## Como executar

**Pré-requisitos:** Python, Google Chrome e acesso autorizado à aplicação de origem.

1. Clone o repositório:

   ```bash
   git clone https://github.com/SEU-USUARIO/automacao-etl-python-selenium.git
   ```

2. Entre na pasta do projeto:

   ```bash
   cd automacao-etl-python-selenium
   ```

3. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   ```

   No Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

5. Crie seu arquivo local `.env` a partir do modelo `.env.example` e configure as credenciais autorizadas. Nunca publique o arquivo `.env`.

6. Execute o ponto de entrada do projeto:

   ```bash
   python main.py
   ```

A execução depende da configuração correta das credenciais, do acesso autorizado à aplicação e da compatibilidade dos seletores com a página de origem.

## Segurança e privacidade

* Credenciais não são armazenadas no código-fonte.
* Dados reais e informações confidenciais não são disponibilizados publicamente.
* A execução deve respeitar as permissões de acesso e as regras de utilização do sistema de origem.
* Os exemplos disponibilizados neste repositório devem utilizar dados fictícios ou devidamente autorizados.

## Observações

Este projeto tem finalidade demonstrativa e de portfólio profissional. A disponibilização do código não implica vínculo, parceria ou endosso oficial pela aplicação ou organização de origem.
