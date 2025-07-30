from spacy.tokens import Doc

from italian_ats_evaluator.models.PosEvaluation import PosEvaluation
from italian_ats_evaluator.models.Span import Span
from italian_ats_evaluator.models.TextEvaluation import TextEvaluation


class PosAnalyzer:

    def analyze(self, text: str, processed_text: Doc, text_evaluation: TextEvaluation) -> PosEvaluation:
        pos_evaluation = PosEvaluation()

        for token in processed_text:
            start = token.idx
            end = start + len(token.text)
            span = Span(start=start, end=end, text=token.text)
            if token.pos_ == "X":
                pos_evaluation.n_other += 1
                pos_evaluation.other.append(span)
            if token.pos_ == "NOUN":
                pos_evaluation.n_nouns += 1
                pos_evaluation.nouns.append(span)
            if token.pos_ == "AUX":
                pos_evaluation.n_verbs += 1
                pos_evaluation.verbs.append(span)
            if token.pos_ == "VERB":
                pos_evaluation.n_verbs += 1
                pos_evaluation.verbs.append(span)
            if token.pos_ == "NUM":
                pos_evaluation.n_number += 1
                pos_evaluation.number.append(span)
            if token.pos_ == "SYM":
                pos_evaluation.n_symbols += 1
                pos_evaluation.symbols.append(span)
            if token.pos_ == "ADV":
                pos_evaluation.n_adverbs += 1
                pos_evaluation.adverbs.append(span)
            if token.pos_ == "DET":
                pos_evaluation.n_articles += 1
                pos_evaluation.articles.append(span)
            if token.pos_ == "PRON":
                pos_evaluation.n_pronouns += 1
                pos_evaluation.pronouns.append(span)
            if token.pos_ == "PART":
                pos_evaluation.n_particles += 1
                pos_evaluation.particles.append(span)
            if token.pos_ == "ADJ":
                pos_evaluation.n_adjectives += 1
                pos_evaluation.adjectives.append(span)
            if token.pos_ == "ADP":
                pos_evaluation.n_prepositions += 1
                pos_evaluation.prepositions.append(span)
            if token.pos_ == "PROPN":
                pos_evaluation.n_proper_nouns += 1
                pos_evaluation.proper_nouns.append(span)
            if token.pos_ == "PUNCT":
                pos_evaluation.n_punctuations += 1
                pos_evaluation.punctuations.append(span)
            if token.pos_ == "INTJ":
                pos_evaluation.n_interjections += 1
                pos_evaluation.interjections.append(span)
            if token.pos_ == "CCONJ":
                pos_evaluation.n_coordinating_conjunctions += 1
                pos_evaluation.coordinating_conjunctions.append(span)
            if token.pos_ == "SCONJ":
                pos_evaluation.n_subordinating_conjunctions += 1
                pos_evaluation.subordinating_conjunctions.append(span)

        return pos_evaluation
