# Baseline results: department

Date: 20 Oct 2026. Numbers are on the validation set (62 rows: 32 own, 30 real_public; 8 per department, 6 for garbage) unless marked as test. The test set is kept for the final evaluation.

Run from the project root:

| Script | Output |
|---|---|
| `python src/baseline_majority.py` | majority baseline on test (run on 16 Oct) |
| `python src/eda_train.py` | text length statistics on train |
| `python src/keyword_explore.py` | keyword candidates per department from train |
| `python src/baseline_keyword.py` | keyword and majority baselines on val, writes `reports/keyword_baseline_val_predictions.csv` |

## Results

| Model | Split | Accuracy | Macro-F1 | Accuracy, 95% bootstrap CI |
|---|---|---|---|---|
| Majority class (roads) | val | 0.129 | 0.029 | 0.05 - 0.21 |
| Keyword rules v1 | val | 0.565 | 0.586 | |
| Keyword rules v1.1 | val | 0.581 | 0.597 | 0.45 - 0.69 |
| Majority class (roads) | test | 0.125 | 0.028 | |

The bootstrap used 10,000 resamples of the 62 val rows (seed 42). The 95% CI of the accuracy difference between keyword rules v1.1 and the majority baseline is 0.29 - 0.60.

Keyword rules v1.1 is the baseline for the next models. With 62 val rows a difference of a few rows is within noise.

## Method

1. For every department, count the number of train complaints that contain each word.
2. Keep a word if it appears in at least 5 complaints of the department and at least 70% of the train complaints containing it belong to that department. Common words such as hai, mein and the fail the second condition.
3. Remove place names and generic words from the candidates by hand: delhi, faridabad, mcf, these, needs, ago, karte, aaya, double, group, pad, off, working, corner, baje, bada, rs. Only the train output was used for this.
4. For a new complaint, count the keyword matches per department and predict the department with the most matches. A tie goes to the department listed first. A complaint with no match is predicted as other.

## Changes from v1 to v1.1

- The tokenizer `\w+` split Hindi words at vowel signs, so "पानी" became "प" and "न". The new `tokenize()` in `src/text_utils.py` keeps Devanagari words whole. Repeating steps 1-2 on train added the keyword "पानी".
- The keyword gadde was a copy mistake; the train word is gaddhe.

Both changes are bug fixes, and the keyword list still comes only from train. The accuracy changed by one row (U48), which is not counted as an improvement.

## Per-class scores (v1.1)

| Department | Precision | Recall | F1 | Val rows |
|---|---|---|---|---|
| electricity | 1.00 | 0.75 | 0.86 | 8 |
| garbage | 0.67 | 0.33 | 0.44 | 6 |
| health | 0.86 | 0.75 | 0.80 | 8 |
| other | 0.24 | 0.75 | 0.36 | 8 |
| pension_govt | 1.00 | 0.50 | 0.67 | 8 |
| police | 0.67 | 0.25 | 0.36 | 8 |
| roads | 0.75 | 0.38 | 0.50 | 8 |
| water_sewage | 0.70 | 0.88 | 0.78 | 8 |

With 8 rows per department, one row changes recall by about 12 points.

Confusion matrix (rows: true label, columns: predicted label):

| true \ pred | electricity | garbage | health | other | pension_govt | police | roads | water_sewage |
|---|---|---|---|---|---|---|---|---|
| electricity | 6 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| garbage | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 2 |
| health | 0 | 0 | 6 | 2 | 0 | 0 | 0 | 0 |
| other | 0 | 0 | 0 | 6 | 0 | 1 | 1 | 0 |
| pension_govt | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0 |
| police | 0 | 0 | 0 | 6 | 0 | 2 | 0 | 0 |
| roads | 0 | 0 | 1 | 3 | 0 | 0 | 3 | 1 |
| water_sewage | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 7 |

Accuracy by source: own 19/32 (0.59), real_public 17/30 (0.57). By language: english 20/32 (0.63), hinglish 14/28 (0.50), hindi 2/2 (too few rows).

## Error analysis

There are 26 errors. 25 rows were predicted as other and 19 of them were wrong.

No keyword matched (19 errors):

| Missing words | Rows |
|---|---|
| kooda, koode | U10 |
| ambulance, behosh | U34 |
| dhamki | U08 |
| ladko, cheda | U11 |
| goli, kaatil | U29 |
| acid, gundo | U28 |
| voter id | U19 |
| awas yojana | U77 |
| chori, FIR | U68 |
| license | U15 |
| voltage, fluctuation | real003, real004 |
| refund, community center | real099 |
| dental, xray | real082 |
| cow dung | real055 |
| lost mobile | real070 |
| road, repaired | real044, real049, U12 |

The word road is not a keyword because it also appears in garbage complaints in train, so its share for roads stayed under 70%. The word repaired does not match repair because words are not reduced to a base form (no stemming).

A keyword pointed to the wrong department (7 errors):

| Row | True | Predicted | Matched word |
|---|---|---|---|
| U07 | garbage | water_sewage | smell |
| real057 | garbage | water_sewage | smell (dead dog) |
| real041 | water_sewage | garbage | badbu |
| U79 | other | police | padosi (encroachment) |
| real121 | other | roads | deep ("deep concern") |
| real046 | roads | health | hospital (part of the address) and repair, a 1-1 tie won by health because it is listed first |
| real051 | roads | water_sewage | supply (road repair after water pipes were laid) |

Notes for the next models:

- Most errors come from words that do not occur in train. Train is mostly synthetic, while val is real and own complaints. TF-IDF with Logistic Regression also learns only train words, so the same rows may stay wrong. A pretrained multilingual model will be compared on these rows later.
- Several no-match rows are high urgency (U34 ambulance, U29 shooting, U28 acid attack). Predicting other for them is the worst kind of error for triage. Rows with no match or low confidence should go to the manual review queue.

## EDA findings (train only)

- Words per complaint: mean 23.0, median 17, maximum 326 (real091). The distribution is right-skewed, so medians are reported as well.
- Median length by source: real_public 68, own 22, real_translated 22, synthetic 16.
- Mean length by language is english 30.0, hinglish 19.5, hindi 18.3, but the medians are 18, 17 and 17. 52 of the 61 real_public train rows are English, so the higher English mean comes from the source, not the language.
- 40 of the 42 Hindi train rows are synthetic.
- The urgency mix is similar across sources (synthetic: 21% high, 26% low, 53% medium; real_public: 25%, 25%, 51%). High-urgency complaints are a little longer (median 19 words, low 15).
- Val complaints are longer than train complaints (mean 48 against 23 words).

## Notes

- The majority baseline was run on test on 16 Oct. Nothing was tuned on it. Further comparisons use val, and every model, including both baselines, is run on test once at the end.
- The keyword lists are frozen. Adding words seen in the val errors would make the val score optimistic.
- Urgency only has the majority baseline so far (test accuracy 0.4375, macro-F1 0.203).
