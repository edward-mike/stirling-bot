from time import sleep

from metrics import evaluate_bertscore, evaluate_meteor, evaluate_rouge
from rich import print as rprint

################################################################
# ToDo.
# 1. Load dataset from directory
# 2. Create Visualizations

################################################################

# reference : human-generated sentence, obtained from dataset.
# llM model should aim to produce this output.
# Load - from data/groundtruth.txt

ground_truth = "stirling strives to ensure that all students can embrace life as part of its vibrant postgraduate community by offering extensive student support services."
testdata = [
    # ground truth, bot response
    (
        ground_truth,
        "Stirling offers a variety of support services for postgraduate students, including academic support, career guidance, counseling services, disability support, and accommodation services. They also have a dedicated student support team to assist with any personal or academic issues that postgraduates may face.",
    ),
    (
        ground_truth,
        "Stirling strives to ensure that all students can embrace life as part of its vibrant postgraduate community by offering extensive student support services.",
    ),
    (
        ground_truth,
        "Stirling offers extensive student support services to ensure that all students can embrace life as part of its vibrant postgraduate community.",
    ),
    (
        ground_truth,
        "Stirling strives to ensure that all students can embrace life as part of its vibrant postgraduate community by offering extensive student support services. These services may include academic support, career guidance, counseling services, and various resources to help postgraduate students succeed in their studies and personal development.",
    ),
    (
        ground_truth,
        "Stirling strives to ensure that all students can embrace life as part of its vibrant postgraduate community by offering extensive student support services.",
    ),
]


if __name__ == "__main__":

    for truth, bot in testdata:
        rprint(f"[bold]ground-truth [/bold]: {truth}")
        rprint(f"[bold]bot response [/bold]: {bot}", end="\n\n")

        # Rouge Metrics.
        evaluate_rouge(bot, truth)
        sleep(1)

        # Meteor Metrics.
        evaluate_meteor(truth, bot)
        sleep(1)

        # BertScore Metrics.
        bot = [bot]
        truth = [truth]
        evaluate_bertscore(bot, truth)
