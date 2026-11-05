import pandas as pd


def main():
    df = pd.read_csv("reports/lr_dept_val_predictions.csv")
    wrong = df[~df["correct"]]
    print(f"wrong: {len(wrong)} of {len(df)}")
    print(wrong[["source", "language", "department", "pred", "complaint_text"]].to_string(max_colwidth=90))
    print()
    print(df.groupby("source")["correct"].mean())
    print()
    print(df.groupby("language")["correct"].mean())


if __name__ == "__main__":
    main()