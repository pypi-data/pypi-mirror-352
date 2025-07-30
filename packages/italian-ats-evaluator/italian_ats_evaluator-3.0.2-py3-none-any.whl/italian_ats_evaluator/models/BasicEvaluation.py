from typing import List, Set

from pydantic import BaseModel, Field


class BasicEvaluation(BaseModel):
    tokens: List[str] = Field(default=[], serialization_alias='tokens')
    tokens_all: List[str] = Field(default=[], serialization_alias='tokensAll')
    chars: List[str] = Field(default=[], serialization_alias='chars')
    chars_all: List[str] = Field(default=[], serialization_alias='charsAll')
    syllables: List[str] = Field(default=[], serialization_alias='syllables')
    words: Set[str] = Field(default=set(), serialization_alias='words')
    lemmas: List[str] = Field(default=[], serialization_alias='lemmas')
    unique_lemmas: Set[str] = Field(default=set(), serialization_alias='uniqueLemmas')
    sentences: List[str] = Field(default=[], serialization_alias='sentences')

    n_tokens: int = Field(default=0, serialization_alias='nTokens')
    n_tokens_all: int = Field(default=0, serialization_alias='nTokensAll')
    n_chars: int = Field(default=0, serialization_alias='nChars')
    n_chars_all: int = Field(default=0, serialization_alias='nCharsAll')
    n_syllables: int = Field(default=0, serialization_alias='nSyllables')
    n_words: int = Field(default=0, serialization_alias='nWords')
    n_unique_lemmas: int = Field(default=0, serialization_alias='nUniqueLemmas')
    n_sentences: int = Field(default=0, serialization_alias='nSentences')
