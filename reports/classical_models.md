# Classical models

All scores are on the validation set (62 rows). The test set is not used until the final evaluation. Confidence intervals are 95% bootstrap intervals (1,000 resamples, seed 42).

## Department: Naive Bayes on TF-IDF

### Setup
- Features: TF-IDF with the shared tokenizer (`src/text_utils.py`), unigrams only, vocabulary of 2,615 words learned from the training set only.
- Model: `MultinomialNB(alpha=1.0)`, no tuning.
- Code: `src/model_nb.py`. Predictions: `reports/nb_dept_val_predictions.csv`.

### Results

| Model | Accuracy | Macro-F1 |
|---|---|---|
| Majority class | 0.129 | 0.029 |
| Keyword rules (v1.1) | 0.581 [0.467, 0.694] | 0.597 [0.452, 0.694] |
| Naive Bayes + TF-IDF | 0.500 [0.371, 0.613] | 0.477 [0.323, 0.577] |

Naive Bayes is above the majority baseline but not above the keyword rules. The difference to the keyword rules (about 5 rows out of 62) is inside the confidence intervals, so it cannot be called a real difference in either direction. It is also not an improvement.

### Per class

| Department | Precision | Recall | F1 | Rows |
|---|---|---|---|---|
| electricity | 0.75 | 0.75 | 0.75 | 8 |
| garbage | 1.00 | 0.33 | 0.50 | 6 |
| health | 0.75 | 0.38 | 0.50 | 8 |
| other | 0.38 | 0.75 | 0.50 | 8 |
| pension_govt | 1.00 | 0.25 | 0.40 | 8 |
| police | 0.33 | 0.12 | 0.18 | 8 |
| roads | 0.50 | 0.38 | 0.43 | 8 |
| water_sewage | 0.38 | 1.00 | 0.55 | 8 |

The model predicted water_sewage 21 times and other 16 times (each class has 8 true rows in val). Together these two classes absorb 37 of the 62 predictions. Police is almost never found (1 of 8).

### By source and language

| Group | Accuracy |
|---|---|
| source: own | 0.469 |
| source: real_public | 0.533 |
| language: english | 0.594 |
| language: hinglish | 0.393 |
| language: hindi | 0.500 (2 rows, not meaningful) |

The model is clearly weaker on Hinglish than on English, and Hinglish is the main language of the project.

### What the model learned
The highest-scoring words per department (`src/nb_top_words.py`) include sensible keywords: paani, water, sewer, ganda, supply (water_sewage); doctor, dispensary, dengue, hospital (health); card, pension, ration, certificate (pension_govt); pothole, gaddha, repair (roads); kachra, waste, badbu (garbage). Police has almost no crime words in its top list (raat, log, kal, karte), so a complaint such as a shooting near a shop gives the model nothing to match.

Common words (hai, se, mein, nahi, din, the) appear in the top list of every department, so the model spends part of its score on words that do not separate the classes.

### Error analysis
Wrongly sent to water_sewage were, among others, a domicile certificate question ("kitne din me aata h"), an ambulance complaint ("nahi aayi"), a power cut ("3 din se ... light jaa rahi h"), two garbage complaints and a shooting report. Several of these use spellings that differ from the training text (h for hai, kia for kiya, gya for gaya), and several share words like din and nahi with the many water-supply templates in train.

What is shown: the model learned sensible keywords for most classes, performs worse on Hinglish, and sends complaints without a strong keyword into water_sewage and other.

What is not yet shown: that common words are the cause of the water_sewage dumping. The top-word lists suggest it but do not prove it. A per-row score breakdown for the wrong rows would.

### Limits
- 62 validation rows: one row moves accuracy by 1.6 points, and class-level numbers rest on 6 to 8 rows.
- 78% of training rows (394 of 506) are synthetic, built from about 85 templates, so the training vocabulary is narrow and short compared to real complaints.
- No tuning has been done yet (alpha, features).

### Next
- Logistic Regression on the same features (4 Nov).
- Character n-grams to handle spelling variants (5 Nov).
- Ablation without translated and synthetic rows (5 Nov).
