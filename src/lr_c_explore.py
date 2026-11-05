import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from baseline_keyword import load_data
from baseline_majority import macro_f1
from text_utils import tokenize


def main():
    train, val = load_data()
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    X_train = vec.fit_transform(train["complaint_text"])
    X_val = vec.transform(val["complaint_text"])

    print("C        train F1   val F1   max prob (val row 0)")
    for C in [10, 100, 1000, 10000, 100000]:
        model = LogisticRegression(C=C, max_iter=5000)
        model.fit(X_train, train["department"])
        pred_train = pd.Series(model.predict(X_train), index=train.index)
        pred_val = pd.Series(model.predict(X_val), index=val.index)
        f1_train = macro_f1(train["department"], pred_train)
        f1_val = macro_f1(val["department"], pred_val)
        top = model.predict_proba(X_val)[0].max()
        print(f"{C:<8} {f1_train:.3f}      {f1_val:.3f}    {top:.3f}")


if __name__ == "__main__":
    main()