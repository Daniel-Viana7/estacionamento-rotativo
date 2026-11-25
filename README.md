# Sistema de Estacionamento Rotativo

Projeto acadêmico da disciplina **Testes e Qualidade de Software na Prática: Da Automação ao CI**. A aplicação simula um estacionamento rotativo simples, com capacidade de 10 veículos e cobrança de R$ 5,00 por hora ou fração.

## Equipe

- Daniel Viana
- Josemir Pedro
- Gabriel Pessoa
- Hélder Gabriel
- José Victor Mendes

## Regras de negócio

As seis funções ficam em `src/estacionamento.py`:

1. `validar_placa`: valida e normaliza placas dos padrões antigo e Mercosul.
2. `verificar_vaga`: verifica se ainda existe vaga disponível.
3. `registrar_entrada`: registra a placa e o horário de entrada, impedindo duplicidade e lotação.
4. `calcular_tempo_permanencia`: calcula o tempo entre entrada e saída em minutos.
5. `calcular_valor`: cobra R$ 5,00 por hora ou fração de hora.
6. `registrar_saida`: calcula a cobrança, encerra o registro e libera a vaga.

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Verifica se a API está ativa. |
| POST | `/entrada` | Registra a entrada de um veículo. Corpo: `{"placa":"ABC1234"}`. |
| GET | `/estacionamentos` | Lista os veículos estacionados. |
| GET | `/estacionamentos/{placa}` | Consulta um veículo pela placa. |
| POST | `/saida/{placa}` | Registra a saída e retorna o tempo e o valor. |
| GET | `/vagas` | Informa capacidade, vagas ocupadas e disponíveis. |

Erros de validação retornam HTTP 400 e veículos não encontrados retornam HTTP 404.

## Preparar o ambiente

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executar a API

```bash
uvicorn src.app:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

## Executar os testes

Somente testes unitários:

```bash
pytest tests/unit -v
```

Somente testes de integração:

```bash
pytest tests/integration -v
```

Todos os testes com cobertura:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

O relatório HTML é gerado na pasta `htmlcov/` (abra `htmlcov/index.html`).

## Integração contínua

O workflow `.github/workflows/ci.yml` é executado em `push` e `pull_request`. O job `integration-tests` depende do sucesso de `unit-tests`. Ao final, o relatório HTML é publicado como artefato `coverage-report` na execução do GitHub Actions.

## Observação

Os dados são mantidos em memória para simplificar a demonstração. Ao reiniciar a API, os registros são apagados.
