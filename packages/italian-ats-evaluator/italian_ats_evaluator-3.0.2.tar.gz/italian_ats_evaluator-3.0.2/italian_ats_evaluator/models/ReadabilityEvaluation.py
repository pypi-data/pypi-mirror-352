from pydantic import BaseModel, Field


class ReadabilityEvaluation(BaseModel):
    ttr: float = Field(default=0.0, serialization_alias='ttr')
    gulpease: float = Field(default=0.0, serialization_alias='gulpease')
    flesch_vacca: float = Field(default=0.0, serialization_alias='fleschVacca')
    lexical_density: float = Field(default=0.0, serialization_alias='lexicalDensity')
