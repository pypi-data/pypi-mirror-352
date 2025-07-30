from spacy.tokens import Doc

from italian_ats_evaluator.models.Span import Span
from italian_ats_evaluator.models.TextEvaluation import TextEvaluation
from italian_ats_evaluator.models.VerbsEvaluation import VerbsEvaluation


class VerbsAnalyzer:

    def analyze(self, text: str, processed_text: Doc, text_evaluation: TextEvaluation) -> VerbsEvaluation:
        verbs_evaluation = VerbsEvaluation()

        verbs = [token for token in processed_text if token.pos_ == "VERB"]
        for verb in verbs:
            children = [c for c in verb.children if c.dep_ == "aux" or c.dep_ == "aux:pass" or c.dep_ == "expl" or c.dep_ == "expl:impers"]
            verb_components = [verb] + children
            verb_components = sorted(verb_components, key=lambda x: x.idx)
            start = verb_components[0].idx
            end = verb_components[-1].idx + len(verb_components[-1].text)
            span = Span(start=start, end=end, text=text[start:end])

            verbs_evaluation.n_verbs += 1
            verbs_evaluation.verbs.append(span)

            if "aux:pass" in [c.dep_ for c in children]:
                verbs_evaluation.n_passive_verbs += 1
                verbs_evaluation.passive_verbs.append(span)
            elif "expl" in [c.dep_ for c in children] or "expl:impers" in [c.dep_ for c in children]:
                verbs_evaluation.n_reflective_verbs += 1
                verbs_evaluation.reflective_verbs.append(span)
            else:
                verbs_evaluation.n_active_verbs += 1
                verbs_evaluation.active_verbs.append(span)

        return verbs_evaluation
