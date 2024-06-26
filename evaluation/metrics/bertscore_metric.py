# https://colab.research.google.com/gist/Abonia1/26c13b7034e85ec1dbe29c2fa0d07242/bertscore-demo.ipynb
# https://medium.com/@abonia/bertscore-explained-in-5-minutes-0b98553bfb71

from bert_score import score
from rich import print as rprint


def evaluate_bertscore(predictions, references):
    """
    Calculate and print BERTScore for a list of predicted responses and their corresponding references.

    Args:
    - predictions (list of str): The predicted responses.
    - references (list of str): The reference sentences.
    """
    # Ensure the predictions and references are lists of strings
    if not isinstance(predictions, list) or not isinstance(references, list):
        raise ValueError("Both predictions and references should be lists of strings.")

    # Calculate BERTScore
    P, R, F1 = score(predictions, references, lang="en", verbose=True)

    # Print the results using rich
    for i, (p, r, f1) in enumerate(zip(P, R, F1)):
        rprint("-" * 20)
        rprint(f"Prediction: {predictions[i]}")
        rprint(f"Reference: {references[i]}")
        rprint(f"BERTScore Precision: {p:.4f}")
        rprint(f"BERTScore Recall: {r:.4f}")
        rprint(f"BERTScore F1: {f1:.4f}")
        rprint("-" * 20)
