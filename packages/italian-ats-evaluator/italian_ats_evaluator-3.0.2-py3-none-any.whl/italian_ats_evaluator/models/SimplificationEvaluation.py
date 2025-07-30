from pydantic import BaseModel, Field

from italian_ats_evaluator.models.DiffEvaluation import DiffEvaluation
from italian_ats_evaluator.models.SimilarityEvaluation import SimilarityEvaluation
from italian_ats_evaluator.models.TextEvaluation import TextEvaluation


class SimplificationEvaluation(BaseModel):
    reference_text_evaluation: TextEvaluation = Field(default=None, serialization_alias="referenceTextEvaluation")
    simplified_text_evaluation: TextEvaluation = Field(default=None, serialization_alias="simplifiedTextEvaluation")

    similarity_evaluation: SimilarityEvaluation = Field(default=None, serialization_alias="similarityEvaluation")
    diff_evaluation: DiffEvaluation = Field(default=None, serialization_alias="diffEvaluation")
