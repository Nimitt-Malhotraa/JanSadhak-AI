import pandas as pd


def load_train():
    return pd.read_csv("data/processed/train.csv", encoding="utf-8-sig")


def add_length(df):
    df["n_words"] = df["complaint_text"].str.split().str.len()
    return df


def length_summary(train):
    print("== words per complaint ==")
    print(train["n_words"].describe().round(1))


def length_by(train, column):
    print(f"\n== words by {column} (mean and median) ==")
    print(train.groupby(column)["n_words"].agg(["count", "mean", "median"]).round(1))


def source_mix(train, column):
    print(f"\n== {column} x source (row counts) ==")
    print(pd.crosstab(train[column], train["source"]))


def longest(train, n=5):
    print(f"\n== {n} longest complaints ==")
    print(train.sort_values("n_words", ascending=False)[["id", "source", "language", "n_words"]].head(n))


def main():
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    train = add_length(load_train())
    length_summary(train)
    length_by(train, "source")
    length_by(train, "language")
    length_by(train, "urgency")
    source_mix(train, "language")
    source_mix(train, "urgency")
    longest(train)


if __name__ == "__main__":
    main()
