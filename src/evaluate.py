import os
import sys

import pandas as pd
import spacy
# from sklearn.metrics import precision_recall_fscore_support # not required any more

# Allow evaluate.py to import detectors.py from the src folder.
sys.path.append(os.path.dirname(__file__))

from detectors import scan_text


def parse_expected_items(row):
    """
    Convert the pipe-separated expected values and subtypes into pairs.

    Example:
        values: Thomas Nandan|EMP-0793
        types:  PERSON_NAME|EMPLOYEE_ID
    """

    expected_values = row["expected_values"]
    expected_subtypes = row["expected_subtypes"]

    if pd.isna(expected_values) or str(expected_values).strip() == "":
        return []

    values = str(expected_values).split("|")
    subtypes = str(expected_subtypes).split("|")

    if len(values) != len(subtypes):
        raise ValueError(
            f"Case {row['case_id']} has different numbers of "
            "expected values and subtypes."
        )

    return list(zip(values, subtypes))


def predicted_items(findings):
    """
    Convert detector findings into comparable text-subtype pairs.
    """

    return [
        (finding["text"], finding["subtype"])
        for finding in findings
    ]


def evaluate_cases(csv_path):
    """
    Run the complete detection pipeline on every labelled test case.
    """

    nlp = spacy.load("en_core_web_sm")
    test_cases = pd.read_csv(csv_path)

    total_tp = 0
    total_fp = 0
    total_fn = 0

    case_results = []

    for _, row in test_cases.iterrows():
        expected = parse_expected_items(row)
        findings = scan_text(row["text"], nlp)
        predicted = predicted_items(findings)

        # Convert to sets for exact text-and-subtype comparison.
        expected_set = set(expected)
        predicted_set = set(predicted)

        true_positives = expected_set & predicted_set
        false_positives = predicted_set - expected_set
        false_negatives = expected_set - predicted_set

        tp = len(true_positives)
        fp = len(false_positives)
        fn = len(false_negatives)

        total_tp += tp
        total_fp += fp
        total_fn += fn

        case_results.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "expected_count": len(expected_set),
                "predicted_count": len(predicted_set),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "expected_items": str(sorted(expected_set)),
                "predicted_items": str(sorted(predicted_set)),
                "missed_items": str(sorted(false_negatives)),
                "unexpected_items": str(sorted(false_positives)),
            }
        )

    precision = (
        total_tp / (total_tp + total_fp)
        if total_tp + total_fp > 0
        else 0.0
    )

    recall = (
        total_tp / (total_tp + total_fn)
        if total_tp + total_fn > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    results_df = pd.DataFrame(case_results)

    return results_df, {
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


if __name__ == "__main__":
    csv_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "tests",
        "test_cases.csv",
    )

    results, metrics = evaluate_cases(csv_path)

    print("\nCase-level evaluation:")
    print(results.to_string(index=False))

    print("\nOverall metrics:")
    print(f"True positives:  {metrics['true_positives']}")
    print(f"False positives: {metrics['false_positives']}")
    print(f"False negatives: {metrics['false_negatives']}")
    print(f"Precision:       {metrics['precision']:.3f}")
    print(f"Recall:          {metrics['recall']:.3f}")
    print(f"F1 score:        {metrics['f1']:.3f}")

    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "tests",
        "evaluation_results.csv",
    )

    results.to_csv(output_path, index=False)

    print(f"\nDetailed results saved to: {output_path}")


