# Meteors

import nltk
from nltk import word_tokenize
from nltk.translate import meteor_score as meteor
from rich import print as rprint

nltk.download("wordnet")


def evaluate_meteor(reference, predicted):
    """
    Calculate and print the METEOR score for a predicted response and its corresponding reference.

    Args:
    - reference (str): The reference sentence.
    - candidate (str): The candidate (predicted) sentence.
    """
    tokenized_reference = word_tokenize(reference)
    tokenized_candidate = word_tokenize(predicted)
    score = meteor.meteor_score([tokenized_reference], tokenized_candidate)
    rprint(f"Meteor Score: {score:.4f}")
