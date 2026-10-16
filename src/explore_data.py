import pandas as pd
train = pd.read_csv("data/processed/train.csv", encoding="utf-8-sig")
test = pd.read_csv("data/processed/test.csv", encoding="utf-8-sig")
print("urgency train" , train["urgency"].value_counts(normalize=True))
print("urgency test" , test["urgency"].value_counts(normalize=True))
print('language train' , train["language"].value_counts(normalize=True))
print('language test' , test["language"].value_counts(normalize=True))
