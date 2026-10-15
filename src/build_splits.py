"""Build the final train / val / test CSVs for JanSadhak AI (v1, 15 Oct 2026).

Inputs
  data/raw/cdi_labeled_full.csv                          synthetic (397 rows; 2 rows with source == own)
  data/raw/own_complaints.csv                            own (80 rows, U01-U80)
  data/raw/jansadhak_real_complaints_clean.csv           real public complaints (131 rows)
  data/raw/jansadhak_real_translated.csv                 Hinglish translations of real rows (88 rows)

Design
  * Synthetic rows are train-only.
  * val and test are class-balanced (10 test + 8 val per department, capped by available own+real rows),
    and stratified inside each department by origin (own/real), urgency and language.
  * 10 own rows go to train; the remaining own+real rows not needed for val/test go to train.
  * A translated row is used only if its real source row is in train (no leakage), and inherits its labels.
  * Any train row that is a near-duplicate (token Jaccard >= 0.6) of a val/test row is dropped from train.
  * Labels for own + real rows follow docs/labeling_rules.md (incl. Rules 10-15).

Run:  python src/build_splits.py
      env JANSADHAK_ROOT overrides the project folder path.
"""
import collections, csv, html, os, random, re

HOME = os.environ.get("HOME", ".")
ROOT = os.environ.get("JANSADHAK_ROOT", f"{HOME}/mnt/JanSadhak-AI")
SEED = 42
TEST_PER_CLASS, VAL_PER_CLASS, OWN_TRAIN_TOTAL = 10, 8, 10
NEAR_DUP = 0.6
LABELED_BY = "rules_2026-10-15"
rng = random.Random(SEED)

DEPT = dict(e="electricity", w="water_sewage", r="roads", g="garbage", p="police", h="health", n="pension_govt", o="other")
URG = dict(l="low", m="medium", h="high")
def parse(s):
    out = {}
    for tok in s.split():
        k, v = tok.split(":"); d, u = v.split("-"); out[k] = (DEPT[d], URG[u])
    return out

REAL_LABELS = parse("""
1:e-m 2:e-m 3:e-m 4:e-m 5:e-m 6:e-l 7:e-m 8:e-l 9:e-m 10:e-l 11:e-m 12:e-h 13:e-m 14:e-l 15:e-l 16:e-m 17:e-l 18:e-m 19:e-m 20:e-m 21:e-m 22:e-m
23:w-m 24:w-m 25:w-h 26:w-m 27:w-h 28:w-m 29:w-m 30:w-m 31:w-h 32:w-h 33:w-m 34:w-h 35:w-h 36:w-h 37:w-m 38:w-m 39:w-m 40:w-m 41:w-h 42:w-l 43:w-m
44:r-l 45:r-l 46:r-m 47:r-l 48:r-l 49:r-l 50:r-l 51:r-l 52:r-m 53:o-m
54:g-m 55:g-m 56:g-m 57:g-m 58:g-m 59:g-m 60:g-l
61:p-m 62:p-m 63:p-m 64:p-m 65:o-l 66:p-m 67:p-h 68:o-l 69:p-l 70:p-l 71:p-m 72:p-h
73:h-m 74:h-l 75:h-l 76:h-h 77:h-m 78:h-l 79:h-h 80:h-m 81:h-m 82:h-l 83:h-m 84:h-l 85:h-m 86:h-h 87:h-h 88:h-h 89:h-h 90:h-h
91:n-l 92:n-l 93:n-l 94:n-l 95:n-m 96:n-h 97:n-h 98:n-h 99:n-l 100:w-l 101:n-l 102:n-m 103:w-l 104:w-l
105:o-h 106:o-m 107:o-h 108:o-m 109:o-h 110:o-l 111:o-l 112:o-m 113:o-m 114:o-m 115:o-l 116:o-m 117:o-m 118:o-m 119:o-m 120:o-m
121:o-l 122:o-l 123:o-m 124:o-l 125:o-l 126:o-m 127:o-m 128:o-l 129:o-h 130:o-m 131:o-m
""")
OWN_LABELS = parse("""
U01:o-m U02:p-m U03:p-m U04:w-m U05:w-l U06:w-l U07:g-m U08:p-h U09:p-h U10:g-m U11:p-h U12:r-l U13:o-l U14:o-l U15:n-m
U16:p-l U17:p-m U18:p-h U19:n-l U20:p-m U21:e-h U22:e-m U23:r-m U24:e-h U25:p-h U26:o-l U27:p-h U28:p-h U29:p-h U30:r-l
U31:h-m U32:h-h U33:h-m U34:h-h U35:h-m U36:h-h U37:h-m U38:g-m U39:g-m U40:g-l U41:n-h U42:n-l U43:n-l U44:r-l U45:r-m
U46:e-l U47:e-m U48:w-h U49:p-h U50:o-m U51:e-m U52:e-h U53:e-h U54:e-l U55:w-m U56:w-h U57:w-m U58:w-m U59:w-h U60:r-h
U61:r-m U62:r-l U63:r-h U64:g-l U65:g-m U66:g-m U67:g-l U68:p-m U69:h-m U70:h-h U71:h-m U72:h-h U73:n-m U74:n-l U75:n-m
U76:n-h U77:n-h U78:p-l U79:o-l U80:o-h
""")
SYN_FIX = {"cdi001": ("roads", "medium", "Rule 5: accident/vehicle damage with no injury stated -> medium")}
SYN_DROP = {"cdi276": "exact duplicate of cdi244"}
# location_mentioned (yes = a specific named place: locality, numbered sector/ward/gali, named landmark, PIN code)
REAL_LOC_YES = set("""3 4 7 12 16 17 18 19 20 22 24 25 26 27 28 29 30 31 33 34 36 37 39 41 43 44 46 47 48 49 50 52 53 54 55 56 57 58
59 60 61 62 63 64 65 67 68 71 72 74 76 78 84 85 90 97 99 104 105 106 107 108 110 111 113 114 117 119 120 121 122 124 125 126 127
128 129 130 131""".split())
OWN_LOC_YES = {"U18", "U44"}
# real rows that were verified=no; source pages re-opened on 15 Oct 2026, opening text + date matched
REVERIFIED = set("22 43 46 47 48 49 50 51 52 53 60 66 67 68 69 70 71".split())
assert len(REAL_LABELS) == 131 and len(OWN_LABELS) == 80

def clean(t, real=False):
    t = re.sub(r"\s+", " ", html.unescape(t or "")).strip()
    if real: t = re.sub(r"\s?br\.\.\.$", "...", t)   # scraped <br> remnant before the site's truncation dots
    return t
def toks(t): return {w for w in re.findall(r"[\wऀ-ॿ]+", t.lower()) if len(w) > 2}
def jac(a, b): return len(a & b) / max(1, len(a | b))
def rd(p): return list(csv.DictReader(open(p, encoding="utf-8-sig")))
def row(**k):
    base = dict(dept_by="given", urg_by="given", orig_dept="", orig_urg="", verification="")
    base.update(k); return base

# ---------------- load ----------------
synthetic, own, changes = [], [], []
for r in rd(f"{ROOT}/data/raw/cdi_labeled_full.csv"):
    if r["id"] in SYN_DROP:
        changes.append([r["id"], "row", "kept", "dropped", SYN_DROP[r["id"]]]); continue
    x = row(id=r["id"], text=clean(r["complaint_text"]), dept=r["department"], urg=r["urgency"], lang=r["language"],
            source=r["source"], loc=r["location_mentioned"], origin="cdi_labeled_full.csv", grp="own" if r["source"] == "own" else "synthetic")
    if r["id"] in SYN_FIX:
        d, u, why = SYN_FIX[r["id"]]
        changes.append([r["id"], "urgency", x["urg"], u, why]); x.update(dept=d, urg=u, urg_by=LABELED_BY, orig_urg=r["urgency"])
    (own if r["source"] == "own" else synthetic).append(x)

for r in rd(f"{ROOT}/data/raw/own_complaints.csv"):   # U01-U80, all written by the project author
    d, u = OWN_LABELS[r["id"]]
    if d != r["category"]: changes.append([r["id"], "department", r["category"], d, "labeling_rules.md"])
    changes.append([r["id"], "urgency", "", u, "labeling_rules.md (new label)"])
    own.append(row(id=r["id"], text=clean(r["complaint_text"]), dept=d, urg=u, lang=r["language"], source="own",
                   loc="yes" if r["id"] in OWN_LOC_YES else "no", origin="own_complaints.csv", grp="own",
                   dept_by=LABELED_BY, urg_by=LABELED_BY, orig_dept=r["category"]))

real = []
for r in rd(f"{ROOT}/data/raw/jansadhak_real_complaints_clean.csv"):
    d, u = REAL_LABELS[r["id"]]
    if d != r["category"]: changes.append([f"real{int(r['id']):03d}", "department", r["category"], d, "labeling_rules.md"])
    changes.append([f"real{int(r['id']):03d}", "urgency", "", u, "labeling_rules.md (new label)"])
    ver = "re-verified 2026-10-15" if r["id"] in REVERIFIED else ("verified" if r["verified"] == "yes" else "UNVERIFIED")
    real.append(row(id=f"real{int(r['id']):03d}", rid=r["id"], text=clean(r["complaint_text"], real=True), dept=d, urg=u, lang=r["language"],
                    source="real_public", loc="yes" if r["id"] in REAL_LOC_YES else "no", origin="jansadhak_real_complaints_clean.csv",
                    grp="real", dept_by=LABELED_BY, urg_by=LABELED_BY, orig_dept=r["category"], verification=ver))
assert len(synthetic) == 394 and len(own) == 82 and len(real) == 131, (len(synthetic), len(own), len(real))
assert all(r["verification"] != "UNVERIFIED" for r in real)

# ---------------- allocation helpers ----------------
def rr(items, key):
    """Order items round-robin across strata so any prefix/slice is a balanced mix."""
    b = collections.defaultdict(list)
    for it in items: b[key(it)].append(it)
    for v in b.values(): rng.shuffle(v)
    keys = sorted(b, key=lambda k: (-len(b[k]), str(k)))
    out = []
    while any(b.values()):
        for k in keys:
            if b[k]: out.append(b[k].pop())
    return out

def deal(items, targets):
    """Assign an ordered list to splits with exact target counts, spreading each split evenly over the list."""
    n = len(items); assert sum(targets.values()) == n, (targets, n)
    got = {s: 0 for s in targets}; out = {s: [] for s in targets}
    for i, it in enumerate(items):
        open_ = [s for s in targets if got[s] < targets[s]]
        s = max(open_, key=lambda s: (targets[s] * (i + 1) / n - got[s], targets[s]))
        got[s] += 1; out[s].append(it)
    return out

def blocks(items, key):
    """Sort items into contiguous strata (random order inside each stratum) so deal() splits every stratum proportionally."""
    return sorted(items, key=lambda r: (key(r), rng.random()))

def imbalance(test, val):
    """Squared distance of val/test from proportional splits on several marginals (lower is better)."""
    def ratio(k):
        if isinstance(k, tuple) and k and k[0] in plan:
            c = k[0]; return plan[c]["test"] / (plan[c]["test"] + plan[c]["val"])
        return len(test) / (len(test) + len(val))
    feats = [lambda r: (r["dept"], r["urg"]), lambda r: (r["dept"], r["grp"]), lambda r: (r["dept"], r["lang"]),
             lambda r: ("_urg", r["urg"]), lambda r: ("_lang", r["lang"]), lambda r: ("_grp", r["grp"]),
             lambda r: ("_ug", r["urg"], r["grp"])]
    score = 0.0
    for f in feats:
        ct = collections.Counter(map(f, test)); cv = collections.Counter(map(f, val))
        for k in set(ct) | set(cv):
            score += (ct[k] - (ct[k] + cv[k]) * ratio(k)) ** 2
    return score

def rebalance(test, val, iters=6000):
    """Hill-climb: swap one test row with one val row of the SAME department if it lowers imbalance."""
    best = imbalance(test, val)
    for _ in range(iters):
        i = rng.randrange(len(test)); c = test[i]["dept"]
        js = [j for j, r in enumerate(val) if r["dept"] == c]
        if not js: continue
        j = rng.choice(js)
        test[i], val[j] = val[j], test[i]
        sc = imbalance(test, val)
        if sc < best: best = sc
        else: test[i], val[j] = val[j], test[i]
    return best

def largest_remainder(weights, total, caps):
    q = {c: 0 for c in weights}
    for _ in range(total):
        c = max((c for c in weights if q[c] < caps[c]), key=lambda c: (weights[c] / (q[c] + 1), weights[c], c))
        q[c] += 1
    return q

# ---------------- split ----------------
pool = collections.defaultdict(lambda: {"own": [], "real": []})
for r in own + real: pool[r["dept"]][r["grp"]].append(r)
plan = {}
for c, p in pool.items():
    n = len(p["own"]) + len(p["real"])
    nt = min(TEST_PER_CLASS, n); nv = min(VAL_PER_CLASS, n - nt)
    plan[c] = dict(n=n, test=nt, val=nv, train=n - nt - nv)
own_train_q = largest_remainder({c: len(pool[c]["own"]) for c in pool}, OWN_TRAIN_TOTAL,
                                {c: min(plan[c]["train"], len(pool[c]["own"])) for c in pool})

S = {"train": list(synthetic), "val": [], "test": []}
for c in sorted(pool):
    p, q = pool[c], plan[c]
    o = rr(p["own"], key=lambda r: r["urg"])
    o_train, o_rest = o[: own_train_q[c]], o[own_train_q[c]:]
    real_train_n = q["train"] - own_train_q[c]
    rl = blocks(p["real"], key=lambda r: (r["urg"], r["lang"]))
    rs = deal(rl, {"train": real_train_n, "eval": len(rl) - real_train_n})
    ev = blocks(o_rest + rs["eval"], key=lambda r: (r["urg"], r["grp"], r["lang"]))
    d = deal(ev, {"test": q["test"], "val": q["val"]})
    S["train"] += o_train + rs["train"]; S["val"] += d["val"]; S["test"] += d["test"]

before = imbalance(S["test"], S["val"])
after = rebalance(S["test"], S["val"])
print(f"val/test imbalance score: {before:.1f} -> {after:.1f}")

# translated rows: only when the real source row is in train; labels inherited from source
train_real = {r["rid"]: r for r in S["train"] if r["grp"] == "real"}
tr_added = tr_skipped = 0
for r in rd(f"{ROOT}/data/raw/jansadhak_real_translated.csv"):
    src = train_real.get(r["source_id"])
    if src is None: tr_skipped += 1; continue
    S["train"].append(row(id=r["id"], text=clean(r["complaint_text"]), dept=src["dept"], urg=src["urg"], lang="hinglish",
                          source="real_translated", loc=src["loc"], origin="jansadhak_real_translated.csv", grp="translated",
                          dept_by=f"inherited:{src['id']}", urg_by=f"inherited:{src['id']}", verification=f"translation of {src['id']}"))
    tr_added += 1

# leakage guard: drop train rows that near-duplicate any val/test row
held = [(r, toks(r["text"])) for s in ("val", "test") for r in S[s]]
kept, dropped = [], []
for r in S["train"]:
    t = toks(r["text"]); hit = next((h for h, ht in held if jac(t, ht) >= NEAR_DUP), None)
    if hit: dropped.append((r, hit))
    else: kept.append(r)
S["train"] = kept
vt = [(a["id"], b["id"]) for a in S["val"] for b in S["test"] if jac(toks(a["text"]), toks(b["text"])) >= NEAR_DUP]

# ---------------- checks ----------------
ids = [r["id"] for s in S for r in S[s]]
assert len(ids) == len(set(ids)), "duplicate ids"
norm = [re.sub(r"\W+", "", r["text"].lower()) for s in S for r in S[s]]
assert len(norm) == len(set(norm)), "duplicate texts"
for s in S:
    for r in S[s]:
        assert r["dept"] in DEPT.values() and r["urg"] in URG.values() and r["lang"] in ("hinglish", "english", "hindi") and r["loc"] in ("yes", "no"), r
        assert r["text"]
assert not any(r["grp"] == "synthetic" for s in ("val", "test") for r in S[s])
assert not any(r["grp"] == "translated" for s in ("val", "test") for r in S[s])

# ---------------- write ----------------
COLS = ["id", "complaint_text", "department", "urgency", "language", "source", "location_mentioned"]
os.makedirs(f"{ROOT}/data/processed", exist_ok=True)
for name in S:
    S[name].sort(key=lambda r: r["id"]); rng.shuffle(S[name])
    with open(f"{ROOT}/data/processed/{name}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(COLS)
        for r in S[name]: w.writerow([r["id"], r["text"], r["dept"], r["urg"], r["lang"], r["source"], r["loc"]])
with open(f"{ROOT}/docs/split_manifest.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["id", "split", "origin_file", "source", "department_set_by", "urgency_set_by", "original_department", "verification"])
    for name in ("train", "val", "test"):
        for r in sorted(S[name], key=lambda r: r["id"]):
            w.writerow([r["id"], name, r["origin"], r["source"], r["dept_by"], r["urg_by"], r["orig_dept"], r["verification"]])
with open(f"{ROOT}/docs/label_changes.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["id", "field", "old_value", "new_value", "reason"]); w.writerows(changes)

# ---------------- report ----------------
print("plan per class:", {c: plan[c] for c in sorted(plan)})
print("own rows in train per class:", dict(sorted(own_train_q.items())))
print(f"translated added {tr_added}, skipped {tr_skipped}; train rows dropped as near-dup of val/test: {len(dropped)}")
for r, h in dropped: print("   dropped", r["id"], "~", h["id"])
print("val-test near-duplicate pairs:", vt)
for name in ("train", "val", "test"):
    rows = S[name]
    print(f"\n== {name}: {len(rows)}")
    for k in ("dept", "urg", "lang", "source", "loc"):
        print(f"   {k:6}", dict(sorted(collections.Counter(r[k] for r in rows).items())))
    if name != "train":
        tab = collections.defaultdict(collections.Counter)
        for r in rows: tab[r["dept"]][r["urg"]] += 1
        print("   dept x urgency:", {c: dict(tab[c]) for c in sorted(tab)})
        g = collections.defaultdict(collections.Counter)
        for r in rows: g[r["dept"]][r["grp"]] += 1
        print("   dept x origin :", {c: dict(g[c]) for c in sorted(g)})
print("\nlabel changes logged:", len(changes), "| department changes:", sum(1 for c in changes if c[1] == "department"))
