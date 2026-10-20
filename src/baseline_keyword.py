import pandas as pd

from baseline_majority import accuracy, macro_f1, majority_baseline, precision_recall_f1
from text_utils import tokenize

RULES = {
    "electricity": ["light", "bill", "streetlight", "streetlights", "meter",
                    "pillar", "reading", "power", "electricity"],
    "garbage": ["kachra", "waste", "uthaya", "garbage", "badbu", "gadi",
                "truck", "dher", "makkhiyan", "dustbin", "khali"],
    "health": ["doctor", "hospital", "dengue", "dispensary", "fogging", "mosquito"],
    "other": ["dogs", "awara", "kutte", "stray", "kutton", "kaat"],
    "pension_govt": ["card", "ration", "pension", "pending", "status", "certificate",
                     "application", "applied", "apply"],
    "police": ["police", "dj", "speaker", "ladkiyon", "padosi"],
    "roads": ["pothole", "gaddha", "gaddhe", "repair", "speed", "footpath", "breaker",
              "deep", "paint", "signal", "patthar", "tar", "accident", "gaadiyan"],
    "water_sewage": ["paani", "pani", "sewer", "supply", "ganda", "sewage", "smell",
                     "naali", "dirty", "beh", "nal", "pipe", "पानी"],
}


def load_data():
    train = pd.read_csv("data/processed/train.csv", encoding="utf-8-sig")
    val = pd.read_csv("data/processed/val.csv", encoding="utf-8-sig")
    return train, val


def predict_department(text, rules, default="other"):
    words = set(tokenize(text))
    best_dept, best_score = default, 0
    for dept, keywords in rules.items():
        score = len(words & set(keywords))
        if score > best_score:
            best_dept, best_score = dept, score
    return best_dept


def print_scores(name, true, pred):
    print(f"{name:9s}: accuracy={accuracy(true, pred):.3f}  macro-F1={macro_f1(true, pred):.3f}")


def print_per_class(true, pred):
    for cls in sorted(true.unique()):
        p, r, f1 = precision_recall_f1(true, pred, cls)
        support = (true == cls).sum()
        print(f"  {cls:14s} P={p:.2f} R={r:.2f} F1={f1:.2f}  rows={support}")


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)

    train, val = load_data()
    true = val["department"]

    pred = val["complaint_text"].apply(lambda t: predict_department(t, RULES))
    _, maj_pred = majority_baseline(train, val, "department")

    print(f"== department, val set ({len(val)} rows) ==")
    print_scores("majority", true, maj_pred)
    print_scores("keywords", true, pred)
    print("keyword rules, per class:")
    print_per_class(true, pred)

    print("\nconfusion matrix (rows = true, columns = predicted):")
    print(pd.crosstab(true, pred, rownames=["true"], colnames=["pred"]))

    pred_other = pred == "other"
    wrong_other = pred_other & (true != "other")
    print(f"\npredicted other: {pred_other.sum()}, wrong: {wrong_other.sum()}")

    val["pred"] = pred
    val["correct"] = val["department"] == val["pred"]
    val[["id", "source", "language", "department", "pred", "correct", "complaint_text"]].to_csv(
        "reports/keyword_baseline_val_predictions.csv", index=False, encoding="utf-8-sig")
    print("saved: reports/keyword_baseline_val_predictions.csv")


if __name__ == "__main__":
    main()
