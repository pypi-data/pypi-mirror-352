from typing import List

from pydantic import BaseModel, Field

from italian_ats_evaluator.models.Span import Span


class PosEvaluation(BaseModel):
    other: List[Span] = Field(default=[], serialization_alias="other")
    nouns: List[Span] = Field(default=[], serialization_alias="nouns")
    verbs: List[Span] = Field(default=[], serialization_alias="verbs")
    number: List[Span] = Field(default=[], serialization_alias="number")
    symbols: List[Span] = Field(default=[], serialization_alias="symbols")
    adverbs: List[Span] = Field(default=[], serialization_alias="adverbs")
    articles: List[Span] = Field(default=[], serialization_alias="articles")
    pronouns: List[Span] = Field(default=[], serialization_alias="pronouns")
    particles: List[Span] = Field(default=[], serialization_alias="particles")
    adjectives: List[Span] = Field(default=[], serialization_alias="adjectives")
    prepositions: List[Span] = Field(default=[], serialization_alias="prepositions")
    proper_nouns: List[Span] = Field(default=[], serialization_alias="properNouns")
    punctuations: List[Span] = Field(default=[], serialization_alias="punctuations")
    interjections: List[Span] = Field(default=[], serialization_alias="interjections")
    coordinating_conjunctions: List[Span] = Field(default=[], serialization_alias="coordinatingConjunctions")
    subordinating_conjunctions: List[Span] = Field(default=[], serialization_alias="subordinatingConjunctions")

    n_other: int = Field(default=0, serialization_alias="nOther")
    n_nouns: int = Field(default=0, serialization_alias="nNouns")
    n_verbs: int = Field(default=0, serialization_alias="nVerbs")
    n_number: int = Field(default=0, serialization_alias="nNumber")
    n_symbols: int = Field(default=0, serialization_alias="nSymbols")
    n_adverbs: int = Field(default=0, serialization_alias="nAdverbs")
    n_articles: int = Field(default=0, serialization_alias="nArticles")
    n_pronouns: int = Field(default=0, serialization_alias="nPronouns")
    n_particles: int = Field(default=0, serialization_alias="nParticles")
    n_adjectives: int = Field(default=0, serialization_alias="nAdjectives")
    n_prepositions: int = Field(default=0, serialization_alias="nPrepositions")
    n_proper_nouns: int = Field(default=0, serialization_alias="nProperNouns")
    n_punctuations: int = Field(default=0, serialization_alias="nPunctuations")
    n_interjections: int = Field(default=0, serialization_alias="nInterjections")
    n_coordinating_conjunctions: int = Field(default=0, serialization_alias="nCoordinatingConjunctions")
    n_subordinating_conjunctions: int = Field(default=0, serialization_alias="nSubordinatingConjunctions")
