from typing import List

from pydantic import BaseModel, Field

from italian_ats_evaluator.models.Span import Span


class LexiconEvaluation(BaseModel):
    juridical_expressions: List[Span] = Field(default=[], serialization_alias='juridicalExpressions')
    difficult_connectives: List[Span] = Field(default=[], serialization_alias='difficultConnectives')
    latinisms: List[Span] = Field(default=[], serialization_alias='latinisms')
    easy_tokens: List[Span] = Field(default=[], serialization_alias='easyTokens')
    easy_fo_tokens: List[Span] = Field(default=[], serialization_alias='easyFoTokens')
    easy_au_tokens: List[Span] = Field(default=[], serialization_alias='easyAuTokens')
    easy_ad_tokens: List[Span] = Field(default=[], serialization_alias='easyAdTokens')

    n_juridical_expressions: int = Field(default=0, serialization_alias='nJuridicalExpressions')
    n_difficult_connectives: int = Field(default=0, serialization_alias='nDifficultConnectives')
    n_latinisms: int = Field(default=0, serialization_alias='nLatinisms')
    n_easy_tokens: int = Field(default=0, serialization_alias='nEasyTokens')
    n_easy_fo_tokens: int = Field(default=0, serialization_alias='nEasyFoTokens')
    n_easy_au_tokens: int = Field(default=0, serialization_alias='nEasyAuTokens')
    n_easy_ad_tokens: int = Field(default=0, serialization_alias='nEasyAdTokens')

