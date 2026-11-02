import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from baseline_keyword import load_data
from text_utils import tokenize


def main():
    train, _ = load_data()
    vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    X_train = vec.fit_transform(train["complaint_text"])
    model = MultinomialNB(alpha=1.0).fit(X_train, train["department"])
    words = vec.get_feature_names_out()
    for i, dept in enumerate(model.classes_):
        top = model.feature_log_prob_[i].argsort()[::-1][:12]
        print(f"{dept:14s}", " ".join(words[top]))


if __name__ == "__main__":
    main()