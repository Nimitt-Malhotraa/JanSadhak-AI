import pandas as pd
def load_data():
    train = pd.read_csv("data/processed/train.csv", encoding="utf-8-sig")
    test = pd.read_csv("data/processed/test.csv", encoding="utf-8-sig")
    return train, test

def majority_baseline(train, test, column):
    majority = train[column].value_counts().idxmax()                          
    predictions = pd.Series(majority, index=test.index)
    return majority, predictions


def accuracy(true, pred):
    return (true == pred).mean()                  

def precision_recall_f1(true, pred, cls):
    tp =  ((true == cls) & (pred == cls)).sum()                                       
    fp = ((true != cls) & (pred == cls)).sum()                                         
    fn = ((true == cls) & (pred != cls)).sum()                                        
    precision = tp/(tp+fp) if(tp +fp)>0 else 0                                 
    recall = tp/(tp+fn) if(tp +fn)>0 else 0                                   
    f1 = 2*(precision*recall)/(precision+recall) if (precision + recall) > 0 else 0                                      
    return precision, recall, f1


def macro_f1(true, pred):
    scores = []
    for cls in sorted(true.unique()):
        _, _, f1 = precision_recall_f1(true, pred, cls)
        scores.append(f1)
    return sum(scores) / len(scores)


def main():
    train, test = load_data()
    for column in ["department", "urgency"]:
        majority, pred = majority_baseline(train, test, column)
        true = test[column]
        p, r, f1 = precision_recall_f1(true, pred, majority)
        print(f"{column}: majority={majority}")
        print(f"  accuracy = {accuracy(true, pred):.4f}")
        print(f"  {majority}: precision={p:.3f} recall={r:.3f} f1={f1:.3f}")
        print(f"  macro-F1 = {macro_f1(true, pred):.4f}")


if __name__ == "__main__":
    main()