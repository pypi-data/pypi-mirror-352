from pydantic import BaseModel, Field


class SimilarityEvaluation(BaseModel):
    semantic_similarity: float = Field(default=0, serialization_alias="semanticSimilarity")
