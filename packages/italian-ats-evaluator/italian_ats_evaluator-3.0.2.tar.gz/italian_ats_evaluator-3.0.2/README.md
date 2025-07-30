# italian-ats-evalautor
This is an open source project to evaluate the performance of an italian ATS (Automatic Text Simplifier) on a set of texts.

You can analyze a single text extracting the following features:
- Overall:
    - Number of tokens
    - Number of tokens (including punctuation)
    - Number of characters
    - Number of characters (including punctuation)
    - Number of words
    - Number of syllables
    - Number of unique lemmas
    - Number of sentences
- Part of Speech (POS) distribution
- Verbs distribution
    - Active Verbs
    - Passive Verbs
    - Reflective Verbs
- Lexicon:
    - Italian Basic Vocabulary (NVdB)
  from [Il Nuovo vocabolario di base della lingua italiana, Tullio De Mauro](https://dizionario.internazionale.it/)
      - All
      - FO (Fundamentals)
      - AU (High Usage)
      - AD (High Availability)
    - Difficult connectives
    - Juridical expressions
    - Latinisms
- Readability:
    - Type-Token Ratio (TTR)
    - Gulpease Index
    - Flesch-Vacca Index
    - Lexical Density

You can also compare two texts and get the following metrics:
- Semantic:
    - Semantic Similarity
- Character diff:
    - Edit Distance
- Token diff:
    - Amount of tokens added
    - Amount of tokens removed
    - Amount of VdB tokens removed
    - Amount of VdB tokens added

## Installation
```bash
pip install italian-ats-evaluator
```

## Usage
Create the `TextAnalyzer` and `SimplificationAnalyzer` objects with the desired models.
```python
from italian_ats_evaluator import TextAnalyzer
from italian_ats_evaluator import SimplificationAnalyzer

text_analyzer = TextAnalyzer(
    spacy_model_name="it_core_news_lg"
)

simplification_analyzer = SimplificationAnalyzer(
    spacy_model_name="it_core_news_lg",
    sentence_transformers_model_name="intfloat/multilingual-e5-base"
)
```

Call the `analyze` method on the `TextAnalyzer` object to evaluate the features of a text.
```python
text_evaluation = text_analyzer.analyze("Il gatto mangia il topo.")
print(text_evaluation)
```

Call the `analyze` method on the `SimplificationAnalyzer` object to evaluate the features of two texts.
```python
simplification_evaluation = simplification_analyzer.analyze(
    reference_text="Il felino mangia il roditore",
    simplified_text="Il gatto mangia il topo"
)
print(simplification_evaluation)
```

## Development
Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the package in editable mode
```bash
pip install -e .
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements
This contribution is a result of the research conducted within the framework of the PRIN 2020 (Progetti di Rilevante Interesse Nazionale) “VerbACxSS: on analytic verbs, complexity, synthetic verbs, and simplification. For accessibility” (Prot. 2020BJKB9M), funded by the Italian Ministero dell’Università e della Ricerca.

## License
[MIT](https://choosealicense.com/licenses/mit/)