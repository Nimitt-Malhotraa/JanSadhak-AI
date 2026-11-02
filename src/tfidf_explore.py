import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from text_utils import tokenize


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


def main():
    train = pd.read_csv(PROCESSED / "train.csv", encoding="utf-8-sig")
    val = pd.read_csv(PROCESSED / "val.csv", encoding="utf-8-sig")
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    X_train = vec.fit_transform(train["complaint_text"])
    X_val = vec.transform(val["complaint_text"])
    print(X_train.shape, X_val.shape)
    words = vec.get_feature_names_out()
    row = X_val[0].toarray()[0]
    top = row.argsort()[::-1][:5]
    print(val["complaint_text"].iloc[0])
    for i in top:
        print(words[i], round(row[i], 3))


if __name__ == "__main__":
    main()