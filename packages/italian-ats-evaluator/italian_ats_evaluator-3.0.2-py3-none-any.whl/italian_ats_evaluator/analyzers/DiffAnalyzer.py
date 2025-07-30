import editdistance

from ..models.BasicEvaluation import BasicEvaluation
from ..models.DiffEvaluation import DiffEvaluation
from ..utils import nlp_utils


class DiffAnalyzer:

    def analyze(self, reference_basic_evaluation: BasicEvaluation, simplified_basic_evaluation: BasicEvaluation) -> DiffEvaluation:
        diff_evaluation = DiffEvaluation()

        diff_evaluation.editdistance = editdistance.eval(
            ''.join(reference_basic_evaluation.chars).lower(),
            ''.join(simplified_basic_evaluation.chars).lower()
        )

        for token, lemma in zip(simplified_basic_evaluation.tokens, simplified_basic_evaluation.lemmas):
            if token not in reference_basic_evaluation.tokens:
                diff_evaluation.n_added_tokens += 1
                diff_evaluation.added_tokens.append(token)
                if nlp_utils.is_vdb(lemma):
                    diff_evaluation.n_added_vdb_tokens += 1
                    diff_evaluation.added_vdb_tokens.append(token)

        for token, lemma in zip(reference_basic_evaluation.tokens, reference_basic_evaluation.lemmas):
            if token not in simplified_basic_evaluation.tokens:
                diff_evaluation.n_deleted_tokens += 1
                diff_evaluation.deleted_tokens.append(token)
                if nlp_utils.is_vdb(lemma):
                    diff_evaluation.n_deleted_vdb_tokens += 1
                    diff_evaluation.deleted_vdb_tokens.append(token)

        return diff_evaluation
