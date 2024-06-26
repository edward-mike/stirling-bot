###################################################################################################################

# https://dev.to/aws-builders/mastering-rouge-matrix-your-guide-to-large-language-model-evaluation-for-summarization-with-examples-jjg
# https://plainenglish.io/community/evaluating-nlp-models-a-comprehensive-guide-to-rouge-bleu-meteor-and-bertscore-metrics-d0f1b1

###################################################################################################################

#################################################### ROUGE-SCORE EVALUATION #######################################

###################################################################################################################

# ROUGE-1 refers to the overlap of unigrams (each word) between the system and reference summaries.
# ROUGE-1 : looks at individual words or unigrams
# ROUGE-2 refers to the overlap of bigrams between the system and reference summaries.
# ROUGE-2 : looks at pairs of words or bigrams
# ROUGE-L: Longest Common Subsequence (LCS)[3] based statistics.
#  Longest common subsequence problem takes into account sentence-level structure similarity
# naturally and identifies longest co-occurring in sequence n-grams automatically.

################################################################################################

from rich import print as rprint
from rouge_score import rouge_scorer


def evaluate_rouge(prediction, ground_truth) -> None:
    """
    Calculate and print the ROUGE scores for a predicted response and its corresponding ground truth.

    Args:
    - prediction (str): The predicted response.
    - ground_truth (str): The ground truth response.
    """
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL", "rougeLsum"], use_stemmer=True
    )
    scores = scorer.score(prediction, ground_truth)
    rprint(scores)
