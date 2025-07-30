from typing import List

from pydantic import BaseModel, Field

from italian_ats_evaluator.models.Span import Span


class VerbsEvaluation(BaseModel):
    verbs: List[Span] = Field(default=[], serialization_alias='verbs')
    active_verbs: List[Span] = Field(default=[], serialization_alias='activeVerbs')
    passive_verbs: List[Span] = Field(default=[], serialization_alias='passiveVerbs')
    reflective_verbs: List[Span] = Field(default=[], serialization_alias='reflectiveVerbs')

    n_verbs: int = Field(default=0, serialization_alias='nVerbs')
    n_active_verbs: int = Field(default=0, serialization_alias='nActiveVerbs')
    n_passive_verbs: int = Field(default=0, serialization_alias='nPassiveVerbs')
    n_reflective_verbs: int = Field(default=0, serialization_alias='nReflectiveVerbs')
