# JanSadhak AI Dataset Card (v1, 15 Oct 2026)

## Files
| File | Rows | Use |
|---|---|---|
| `data/processed/train.csv` | 506 | Model training only |
| `data/processed/val.csv` | 62 | Model selection and tuning |
| `data/processed/test.csv` | 80 | Final evaluation only. Do not look at it while building models. |
| `docs/split_manifest.csv` | 648 | Origin, split, who set each label, verification status of every row |
| `docs/label_changes.csv` | 225 | Every label that was added or changed while building v1, with the reason |
| `src/build_splits.py` | - | Rebuilds the three files exactly (seed 42) |

Columns (same in all three files): `id, complaint_text, department, urgency, language, source, location_mentioned`

## Sources
| Source | Rows used | Where they go |
|---|---|---|
| Synthetic (`cdi_labeled_full.csv`, `source` = synthetic / synthetic_edited) | 394 of 397 | Train only. 2 rows with `source = own` moved to the own group; `cdi276` dropped as an exact duplicate of `cdi244`. |
| Own (`data/raw/own_complaints.csv` 80 rows, ids U01-U80 + the 2 own rows above) | 82 | 10 train, 32 val, 40 test |
| Real public complaints (`jansadhak_real_complaints_clean.csv`) | 131 of 131 | 61 train, 30 val, 40 test |
| Real, translated to Hinglish (`jansadhak_real_translated.csv`) | 41 of 88 | Train only, and only when the original real row is also in train |

All 131 real complaints come from public pages on consumercomplaints.in.

## How the split was made
1. Synthetic and translated rows are train-only.
2. Val and test are class-balanced: 10 test and 8 val rows per department (garbage has only 16 own+real rows, so it gets 10 test and 6 val).
3. Inside each department, rows are split proportionally by urgency, origin (own/real) and language, then a balancing pass swaps val/test rows of the same department to make their mixes match.
4. Remaining own+real rows go to train (10 own rows in total).
5. Leakage checks: no shared ids or texts between splits, no train row with token Jaccard >= 0.6 to any val/test row, and no translation whose original is in val/test.

## Label distribution
| Split | high | medium | low | english | hinglish | hindi |
|---|---|---|---|---|---|---|
| train | 112 | 264 | 130 | 173 | 291 | 42 |
| val | 15 | 28 | 19 | 32 | 28 | 2 |
| test | 20 | 35 | 25 | 41 | 37 | 2 |

Departments: test has 10 per department; val has 8 per department (garbage 6).

## Labels
- Synthetic rows keep their original labels, except `cdi001` (urgency high -> medium, Rule 5).
- For own and real rows, department and urgency were set on 15 Oct 2026 by Claude following `docs/labeling_rules.md` (Rules 1-15). 12 departments changed from the original category; all changes are listed in `docs/label_changes.csv`.
- These labels have been reviewed by Nimitt Malhotra (15 Oct 2026).
- `location_mentioned` = yes when a specific named place appears (locality, numbered sector/ward/gali, named landmark, PIN code). Set by hand for own and real rows; original values kept for synthetic rows.

## Borderline labels
These rows could reasonably get a different label under the rules. They are kept as labeled, and errors on them should be read with care.

| id | split | department | urgency | Why borderline |
|---|---|---|---|---|
| U49 | test | police | high | urgency judgement (Rules 1-15), to be re-checked in the label self-check |
| U61 | test | roads | medium | urgency judgement, to be re-checked |
| U66 | test | garbage | medium | urgency judgement, to be re-checked |
| real083 | test | health | medium | urgency judgement, to be re-checked |
| real107 | test | other | high | urgency judgement, to be re-checked |
| real091 | train | pension_govt | low | multi-issue complaint: birth certificate delay (pension_govt, Rule 6) and rude hospital staff (health, Rule 15); labeled by the main issue |

## Known limitations
- Small evaluation sets: 10 test rows per department means one mistake moves that department's recall by 10 points. Report bootstrap 95% confidence intervals with every F1 score.
- Only 4 Hindi (Devanagari) rows are in val + test, so Hindi performance cannot be measured reliably.
- Real complaints are mostly formal English and many are cut off by the website (they end in "..."). The `[name]`, `[phone]`, `[protected]` markers are redactions and are kept on purpose.
- Garbage has no own or real rows in train; the model learns garbage only from synthetic data.
- Length shift: train complaints average 23 words (median 17) because 391 of 506 rows are short synthetic texts (median 16), while val averages 48 words (real_public median 61.5). Models trained on short template text may do worse on long, messy real complaints (src/eda_train.py).
- The synthetic data was generated from about 85 templates (`src/make_synthetic_data.py`), so many rows are near-paraphrases of each other. They are all in train. Accuracy measured on synthetic rows will be optimistic.
- 41 real complaints appear in train twice: the English original and its Hinglish translation (`source = real_translated`). Do not run k-fold cross-validation on train, because a fold could hold the original while another fold holds its translation. Tune on `val.csv` only. Whether the translations help is an open question to be tested with an ablation (train with and without them).

## How to evaluate
- Primary metric: macro-F1, separately for department and urgency.
- Also report per-class precision/recall/F1, the confusion matrix, and scores split by `source` (own vs real_public) and by `language`.
- Every model, including the dumb baseline, is evaluated on the same test file once, at the end.
