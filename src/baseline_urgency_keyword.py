import pandas as pd

from baseline_keyword import load_data, print_scores, print_per_class
from baseline_majority import majority_baseline
from text_utils import tokenize

HIGH_WORDS = ["gir", "lagi", "aag", "bachche", "buzurg", "pareshan", "logon", "kaat",
              "cases", "bimar", "dengue", "hospital", "ladkiyon", "chot", "ghayal"]
LOW_WORDS = ["karwa", "dijiye", "footpath", "streetlight", "date", "kam"]


def predict_urgency(text, high_words, low_words, default="medium"):
    words = set(tokenize(text))
    if words & set(high_words):
        return "high"
    if words & set(low_words):
        return "low"
    return default


def main():
    pd.set_option("display.width", 250)
    train, val = load_data()
    true = val["urgency"]

    pred = val["complaint_text"].apply(lambda t: predict_urgency(t, HIGH_WORDS, LOW_WORDS))
    _, maj_pred = majority_baseline(train, val, "urgency")

    print(f"== urgency, val set ({len(val)} rows) ==")
    print_scores("majority", true, maj_pred)
    print_scores("keywords", true, pred)
    print("keyword rules, per class:")
    print_per_class(true, pred)
    print("\nconfusion matrix (rows = true, columns = predicted):")
    print(pd.crosstab(true, pred, rownames=["true"], colnames=["pred"]))

    val["pred"] = pred
    val["correct"] = val["urgency"] == val["pred"]
    val[["id", "source", "language", "urgency", "pred", "correct", "complaint_text"]].to_csv(
    "reports/urgency_keyword_val_predictions.csv", index=False, encoding="utf-8-sig")      


if __name__ == "__main__":
    main()
