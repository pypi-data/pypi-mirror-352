from typing import List

from pydantic import BaseModel, Field


class DiffEvaluation(BaseModel):
    editdistance: int = Field(default=0, serialization_alias="editDistance")

    added_tokens: List[str] = Field(default=[], serialization_alias="addedTokens")
    deleted_tokens: List[str] = Field(default=[], serialization_alias="deletedTokens")
    added_vdb_tokens: List[str] = Field(default=[], serialization_alias="addedVdbTokens")
    deleted_vdb_tokens: List[str] = Field(default=[], serialization_alias="deletedVdbTokens")

    n_added_tokens: int = Field(default=0, serialization_alias="nAddedTokens")
    n_deleted_tokens: int = Field(default=0, serialization_alias="nDeletedTokens")
    n_added_vdb_tokens: int = Field(default=0, serialization_alias="nAddedVdbTokens")
    n_deleted_vdb_tokens: int = Field(default=0, serialization_alias="nDeletedVdbTokens")
