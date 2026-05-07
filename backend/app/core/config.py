# Tabela regressiva de IR em dias corridos (proxy: 1 mês = 30 dias)
IR_TABLE = [
    (180, 0.225),
    (360, 0.200),
    (720, 0.175),
    (float("inf"), 0.150),
]

# Classificação tributária
TAXED_ASSETS = {
    "CDB",
    "LC",
    "RDB",
    "TESOURO_SELIC",
    "TESOURO_IPCA",
    "TESOURO_PREFIXADO",
    "DEBENTURE",
}

EXEMPT_ASSETS = {
    "LCI",
    "LCA",
    "CRI",
    "CRA",
    "DEBENTURE_INCENTIVADA",
    "POUPANCA",  # isenta, mas com taxa calculada internamente
}

# Limite da Selic para regra da Poupança
POUPANCA_SELIC_THRESHOLD = 8.5  # % a.a.
POUPANCA_FIXED_MONTHLY = 0.005  # 0.5% a.m. (quando Selic <= 8.5%)

# URLs das APIs do Banco Central do Brasil
BCB_SELIC_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
BCB_IPCA_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/12?formato=json"

# Cache TTL em segundos (1 hora)
CACHE_TTL_SECONDS = 3600

# Versão da API
API_VERSION = "1.0.0"
