from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AssetType(str, Enum):
    # Tributados regressivos
    CDB = "CDB"
    LC = "LC"
    RDB = "RDB"
    TESOURO_SELIC = "TESOURO_SELIC"
    TESOURO_IPCA = "TESOURO_IPCA"  # taxa = spread sobre IPCA
    TESOURO_PREFIXADO = "TESOURO_PREFIXADO"
    DEBENTURE = "DEBENTURE"
    # Isentos
    LCI = "LCI"
    LCA = "LCA"
    CRI = "CRI"
    CRA = "CRA"
    DEBENTURE_INCENTIVADA = "DEBENTURE_INCENTIVADA"
    POUPANCA = "POUPANCA"  # taxa calculada internamente


class SimulationInput(BaseModel):
    asset_type: AssetType
    initial_value: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    annual_rate: float = Field(
        gt=0, description="Taxa anual em %. Ignorada para POUPANCA."
    )
    period_months: int = Field(ge=1, le=600)

    # Campo extra: spread para TESOURO_IPCA
    # Ex: IPCA + 6% a.a. -> annual_rate = 6.0, o servico busca IPCA e soma
    ipca_spread: float = Field(
        default=0.0,
        ge=0,
        description="Spread sobre IPCA para TESOURO_IPCA (% a.a.)",
    )

    @model_validator(mode="after")
    def at_least_one_value(self):
        if self.initial_value == 0 and self.monthly_contribution == 0:
            raise ValueError("Informe ao menos initial_value ou monthly_contribution > 0.")
        return self
