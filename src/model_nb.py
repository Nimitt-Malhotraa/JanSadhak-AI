import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from baseline_keyword import load_data, print_scores, print_per_class
from baseline_majority import accuracy, macro_f1
from bootstrap_ci import bootstrap_ci
from text_utils import tokenize


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    train, val = load_data()
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    X_train = vec.fit_transform(train["complaint_text"])
    X_val = vec.transform(val["complaint_text"])

    model = MultinomialNB(alpha= 1.0)
    model.fit(X_train, train["department"])
    pred = pd.Series(model.predict(X_val), index=val.index)
    true = val["department"]

    print(f"== department, val set ({len(val)} rows) ==")
    print_scores("naive bayes", true, pred)
    for name, metric in [("accuracy", accuracy), ("macro-F1", macro_f1)]:
        low, high = bootstrap_ci(true, pred, metric)
        print(f"{name}: {metric(true, pred):.3f}  95% CI [{low:.3f}, {high:.3f}]")
    print("per class:")
    print_per_class(true, pred)
    print("\nconfusion matrix (rows = true, columns = predicted):")
    print(pd.crosstab(true, pred, rownames=["true"], colnames=["pred"]))

    val["pred"] = pred
    val["correct"] = val["department"] == val["pred"]
    val[["id", "source", "language", "department", "pred", "correct", "complaint_text"]].to_csv(
        "reports/nb_dept_val_predictions.csv", index=False, encoding="utf-8-sig")
    print("saved: reports/nb_dept_val_predictions.csv")


if __name__ == "__main__":
    main()