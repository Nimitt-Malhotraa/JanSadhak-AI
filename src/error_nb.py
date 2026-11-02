import pandas as pd


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 110)
    df = pd.read_csv("reports/nb_dept_val_predictions.csv", encoding="utf-8-sig")

    print("accuracy by source:")
    print(df.groupby("source")["correct"].mean())
    print("\naccuracy by language:")
    print(df.groupby("language")["correct"].mean())

    print("\nwhat the model predicted:")
    print(df["pred"].value_counts())

    wrong_water = df[(df["pred"] == "water_sewage") & (~df["correct"])]
    print("\nwrongly sent to water_sewage:")
    print(wrong_water[["id", "department", "complaint_text"]].to_string(index=False))


if __name__ == "__main__":
    main()