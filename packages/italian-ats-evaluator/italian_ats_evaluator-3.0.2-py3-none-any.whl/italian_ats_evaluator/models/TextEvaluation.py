from pydantic import BaseModel, Field

from italian_ats_evaluator.models.BasicEvaluation import BasicEvaluation
from italian_ats_evaluator.models.LexiconEvaluation import LexiconEvaluation
from italian_ats_evaluator.models.PosEvaluation import PosEvaluation
from italian_ats_evaluator.models.ReadabilityEvaluation import ReadabilityEvaluation
from italian_ats_evaluator.models.VerbsEvaluation import VerbsEvaluation


class TextEvaluation(BaseModel):
    basic_evaluation: BasicEvaluation = Field(default=None, serialization_alias="basicEvaluation")
    pos_evaluation: PosEvaluation = Field(default=None, serialization_alias="posEvaluation")
    verbs_evaluation: VerbsEvaluation = Field(default=None, serialization_alias="verbsEvaluation")
    lexicon_evaluation: LexiconEvaluation = Field(default=None, serialization_alias="lexiconEvaluation")
    readability_evaluation: ReadabilityEvaluation = Field(default=None, serialization_alias="readabilityEvaluation")
