from .analyzers.BasicAnalyzer import BasicAnalyzer
from .analyzers.LexiconAnalyzer import LexiconAnalyzer
from .analyzers.PosAnalyzer import PosAnalyzer
from .analyzers.ReadabilityAnalyzer import ReadabilityAnalyzer
from .analyzers.VerbsAnalyzer import VerbsAnalyzer
from .models.TextEvaluation import TextEvaluation
from .utils import nlp_utils


class TextAnalyzer:
    def __init__(self, spacy_model_name: str = nlp_utils.DEFAULT_SPACY_MODEL):
        self.nlp_model = nlp_utils.get_spacy_model(spacy_model_name)

        self.basic_analyzer = BasicAnalyzer()
        self.pos_analyzer = PosAnalyzer()
        self.verb_analyzer = VerbsAnalyzer()
        self.lexicon_analyzer = LexiconAnalyzer()
        self.readability_analyzer = ReadabilityAnalyzer()

    def analyze(self, text: str) -> TextEvaluation:
        text_processed = self.nlp_model(text)

        text_evaluation = TextEvaluation()
        text_evaluation.basic_evaluation = self.basic_analyzer.analyze(text, text_processed, text_evaluation)
        text_evaluation.pos_evaluation = self.pos_analyzer.analyze(text, text_processed, text_evaluation)
        text_evaluation.verbs_evaluation = self.verb_analyzer.analyze(text, text_processed, text_evaluation)
        text_evaluation.lexicon_evaluation = self.lexicon_analyzer.analyze(text, text_processed, text_evaluation)
        text_evaluation.readability_evaluation = self.readability_analyzer.analyze(text, text_processed, text_evaluation)

        return text_evaluation
