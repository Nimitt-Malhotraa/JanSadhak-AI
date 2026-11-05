import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from baseline_keyword import load_data, print_scores, print_per_class
from baseline_majority import accuracy, macro_f1
from bootstrap_ci import bootstrap_ci
from text_utils import tokenize


def main():
    pd.set_option("display.width", 250)
    train, val = load_data()
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    X_train = vec.fit_transform(train["complaint_text"])
    X_val = vec.transform(val["complaint_text"])
    true = val["urgency"]

    print("C        train F1   val F1")
    for C in [1, 10, 100, 1000]:
        model = LogisticRegression(C=C, max_iter=5000)
        model.fit(X_train, train["urgency"])
        pred_train = pd.Series(model.predict(X_train), index=train.index)
        pred_val = pd.Series(model.predict(X_val), index=val.index)
        f1_train = macro_f1(train["urgency"], pred_train)
        f1_val = macro_f1(true, pred_val)
        print(f"{C:<8} {f1_train:.3f}      {f1_val:.3f}")

    model = LogisticRegression(C=100, max_iter=5000)
    model.fit(X_train, train["urgency"])
    pred = pd.Series(model.predict(X_val), index=val.index)

    print(f"\n== urgency, val set ({len(val)} rows), C=100 ==")
    print_scores("logistic regression", true, pred)
    for name, metric in [("accuracy", accuracy), ("macro-F1", macro_f1)]:
        low, high = bootstrap_ci(true, pred, metric)
        print(f"{name}: {metric(true, pred):.3f}  95% CI [{low:.3f}, {high:.3f}]")
    print("per class:")
    print_per_class(true, pred)
    print("\nconfusion matrix (rows = true, columns = predicted):")
    print(pd.crosstab(true, pred, rownames=["true"], colnames=["pred"]))


if __name__ == "__main__":
    main()
    