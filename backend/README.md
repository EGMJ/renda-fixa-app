# Renda Fixa API

Motor financeiro stateless para simulação de investimentos em renda fixa brasileira.

## Stack Tecnológica

- **Python 3.10+**
- **FastAPI** - Framework web assíncrono
- **Pydantic v2** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **httpx** - Cliente HTTP assíncrono (APIs do BCB)
- **pytest + pytest-asyncio** - Testes

## Estrutura

```
backend/
  ├── app/
  │   ├── core/config.py         # Constantes e configurações
  │   ├── models/                # Schemas Pydantic
  │   ├── services/              # Lógica de negócio
  │   │   ├── calculator.py      # Motor PEPS
  │   │   ├── tax_engine.py      # Cálculo de IR
  │   │   ├── asset_classifier.py # Classificação de ativos
  │   │   └── market_data.py     # Integração BCB
  │   ├── api/v1/routes.py       # Endpoints
  │   └── main.py                # Aplicação FastAPI
  ├── tests/                     # Suite de testes
  └── requirements.txt
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Execução

```bash
# Desenvolvimento (recarga automática)
uvicorn app.main:app --reload --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/assets` | GET | Lista de ativos disponíveis |
| `/api/v1/market-rates` | GET | Taxas atuais (Selic, IPCA, Poupança) |
| `/api/v1/simulate` | POST | Executa simulação |

## Exemplo de Request

```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "CDB",
    "initial_value": 1000,
    "monthly_contribution": 100,
    "annual_rate": 12.0,
    "period_months": 24
  }'
```

## Exemplo de Response

```json
{
  "total_invested": 3300.00,
  "gross_balance": 3654.32,
  "gross_return": 354.32,
  "total_ir": 53.15,
  "net_balance": 3601.17,
  "net_return": 301.17,
  "net_return_pct": 9.13,
  "effective_annual_rate": 10.24,
  "ir_effective_rate": 15.00,
  "rate_info": {
    "selic_rate_pct": null,
    "ipca_rate_pct": null,
    "effective_monthly_pct": 0.95,
    "effective_annual_pct": 12.00
  },
  "tax_breakdown": [...],
  "monthly_evolution": [...]
}
```

## Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=term-missing

# Testes específicos
pytest tests/test_tax_engine.py -v
pytest tests/test_calculator.py -v
pytest tests/test_market_data.py -v
pytest tests/test_routes.py -v
```

## Características

- **Motor PEPS**: Cálculo de IR individual por aporte (FIFO)
- **Tabela regressiva**: Alíquotas por dias de detenção (22.5% → 15%)
- **Ativos especiais**: Poupança (regra dinâmica), Tesouro IPCA+ (composição real)
- **Cache BCB**: 1 hora TTL para Selic/IPCA
- **Stateless**: Sem banco de dados, cálculos em memória

## Ativos Suportados

**Tributados (IR regressivo):**
- CDB, LC, RDB
- Tesouro Selic, Tesouro IPCA+, Tesouro Prefixado
- Debêntures

**Isentos:**
- LCI, LCA, CRI, CRA
- Debêntures Incentivadas
- Poupança (rendimento dinâmico)
