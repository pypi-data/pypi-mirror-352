from .TextAnalyzer import TextAnalyzer
from .analyzers.DiffAnalyzer import DiffAnalyzer
from .analyzers.SimilarityAnalyzer import SimilarityAnalyzer
from .models.SimplificationEvaluation import SimplificationEvaluation
from .utils import nlp_utils


class SimplificationAnalyzer:
    def __init__(self,
                 spacy_model_name: str = nlp_utils.DEFAULT_SPACY_MODEL,
                 sentence_transformers_model_name: str = nlp_utils.DEFAULT_SENTENCE_TRANSFORMERS_MODEL):

        self.text_analyzer = TextAnalyzer(spacy_model_name)
        self.similarity_analyzer = SimilarityAnalyzer(sentence_transformers_model_name)
        self.diff_analyzer = DiffAnalyzer()

    def analyze(self, reference_text: str, simplified_text: str) -> SimplificationEvaluation:
        simplification_evaluation = SimplificationEvaluation()

        simplification_evaluation.reference_text_evaluation = self.text_analyzer.analyze(reference_text)
        simplification_evaluation.simplified_text_evaluation = self.text_analyzer.analyze(simplified_text)

        simplification_evaluation.similarity_evaluation = self.similarity_analyzer.analyze(reference_text, simplified_text)
        simplification_evaluation.diff_evaluation = self.diff_analyzer.analyze(simplification_evaluation.reference_text_evaluation.basic_evaluation,
                                                                               simplification_evaluation.simplified_text_evaluation.basic_evaluation)

        return simplification_evaluation
