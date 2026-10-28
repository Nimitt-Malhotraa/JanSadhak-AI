from collections import Counter

import pandas as pd

from text_utils import tokenize


def load_train():
    return pd.read_csv("data/processed/train.csv", encoding="utf-8-sig")


def count_words(train, column):
    counters = {}
    for urg in sorted(train[column].unique()):
        counters[urg] = Counter()
        texts = train[train[column] == urg]["complaint_text"]
        for text in texts:
            counters[urg].update(set(tokenize(text)))
    return counters


def distinctive_words(counters, urg, min_count=5, min_precision=0.7):
    result = []
    for word, count in counters[urg].items():
        total = sum(c[word] for c in counters.values())
        precision = count / total
        if count >= min_count and precision >= min_precision:
            result.append((word, count, round(precision, 2)))
    return sorted(result, key=lambda item: item[1], reverse=True)


def main():
    train = load_train()
    counters = count_words(train, "urgency")
    for urg in counters:
        print(urg, distinctive_words(counters, urg))


if __name__ == "__main__":
    main()
