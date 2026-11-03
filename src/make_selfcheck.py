from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "selfcheck"
N_ROWS = 65
SEED = 42


def load_all():
    parts = [
        pd.read_csv(PROCESSED / f"{name}.csv", encoding="utf-8-sig")
        for name in ["train", "val", "test"]
    ]
    return pd.concat(parts, ignore_index=True)


def main():
    df = load_all()
    human = df[df["source"].isin(["own", "real_public"])]
    sample = human.sample(n= N_ROWS, random_state= SEED)
    blank = sample[["id", "complaint_text"]].copy()
    blank["department"] = ""
    blank["urgency"] = ""
    key = sample[["id", "department", "urgency"]]
    OUT.mkdir(parents=True, exist_ok=True)
    blank.to_csv(OUT / "selfcheck_blank.csv", index=False, encoding="utf-8-sig")
    key.to_csv(OUT / "selfcheck_key.csv", index=False, encoding= "utf-8-sig")
    print(len(blank), "rows written to", OUT)


if __name__ == "__main__":
    main()