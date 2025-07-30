from spacy.tokens import Doc

from ..models.BasicEvaluation import BasicEvaluation
from ..models.PosEvaluation import PosEvaluation
from ..models.ReadabilityEvaluation import ReadabilityEvaluation
from ..models.TextEvaluation import TextEvaluation


class ReadabilityAnalyzer:

    def analyze(self, text: str, processed_text: Doc, text_evaluation: TextEvaluation) -> ReadabilityEvaluation:
        readability_evaluation = ReadabilityEvaluation()

        readability_evaluation.ttr = self.__eval_ttr(text_evaluation.basic_evaluation)
        readability_evaluation.gulpease = self.__eval_gulpease(text_evaluation.basic_evaluation)
        readability_evaluation.flesch_vacca = self.__eval_flesch_vacca(text_evaluation.basic_evaluation)
        readability_evaluation.lexical_density = self.__eval_lexical_density(text_evaluation.basic_evaluation, text_evaluation.pos_evaluation)

        return readability_evaluation

    @staticmethod
    def __eval_ttr(basic_evaluation: BasicEvaluation) -> float:
        return float(basic_evaluation.n_words) / basic_evaluation.n_tokens * 100.0

    @staticmethod
    def __eval_gulpease(basic_evaluation: BasicEvaluation) -> float:
        return 89 + \
                ((300.0 * basic_evaluation.n_sentences) - (10.0 * basic_evaluation.n_chars)) / float(basic_evaluation.n_tokens)

    @staticmethod
    def __eval_flesch_vacca(basic_evaluation: BasicEvaluation) -> float:
        return 206 - \
                (0.65 * (basic_evaluation.n_syllables / basic_evaluation.n_tokens) * 100.0) - \
                (1.0 * (basic_evaluation.n_tokens / basic_evaluation.n_sentences))

    @staticmethod
    def __eval_lexical_density(basic_evaluation: BasicEvaluation, pos_evaluation: PosEvaluation) -> float:
        return (pos_evaluation.n_nouns + pos_evaluation.n_adverbs + pos_evaluation.n_adjectives + pos_evaluation.n_verbs) / basic_evaluation.n_tokens * 100.0
