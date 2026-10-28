import numpy as np
import pandas as pd
from baseline_majority import accuracy, macro_f1

def bootstrap_ci(true, pred, metric, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(true)
    scores = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        scores.append(metric(true.iloc[idx], pred.iloc[idx]))
    low, high = np.percentile(scores, [2.5, 97.5])
    return low, high


RUNS = [("department", "reports/keyword_baseline_val_predictions.csv"),
        ("urgency", "reports/urgency_keyword_val_predictions.csv")]


def main():
    for column, path in RUNS:
        df = pd.read_csv(path, encoding="utf-8-sig")
        true, pred = df[column], df["pred"]
        print(f"== {column} ==")
        for name, metric in [("accuracy", accuracy), ("macro-F1", macro_f1)]:
            low, high = bootstrap_ci(true, pred, metric)
            print(f"{name}: {metric(true, pred):.3f}  95% CI [{low:.3f}, {high:.3f}]")


if __name__ == "__main__":
    main()