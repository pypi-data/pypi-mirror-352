from sklearn.metrics import accuracy_score, classification_report, f1_score
from collections import defaultdict

tags = {"NOUN","VERB","ADJ","ADV","PROPN"}
lex = open("C:\\Uni\\Hebrew\\HebPipe.git\\hebpipe\\data\\heb.lex",encoding="utf8").read().strip().split("\n")
lex = [l for l in lex if "\t" in l]
lex = [l for l in lex if l.split("\t")[1] in tags]
lex = {l.split("\t")[0] + "\t" + l.split("\t")[1]:l.split("\t")[2] for l in lex if "\t" in l}

def clean_final(text):
    finals = {"פ": "ף", "כ": "ך", "מ": "ם", "נ": "ן", "צ": "ץ"}
    if text[-1] in finals:
        text = text[:-1] + finals[text[-1]]
    return text


def post_process(word, pos, lemma, morph):
    if "Plur" in morph and word == lemma and pos in ["NOUN", "ADJ"] and (word.endswith("ים") or word.endswith("ות")):
        lemma = lemma[:-2]
        if word.endswith("ות"):
            lemma += "ה"
        lemma = clean_final(lemma)
    #if "Fem" in morph and pos == "ADJ" and word.endswith("ית") and lemma == word:
    #    lemma = lemma[:-1]
    if "Fem" in morph and word == lemma:
        if word + "\t" + pos in lex:
            pass
            #lemma = lex[word+"\t"+pos]
    if word == lemma:
        if word + "\t" + pos in lex:
            if pos == "VERB" and "Fut" in morph:
                lemma = lex[word + "\t" + pos]
            if pos == "VERB" and "Pres" in morph:
                lemma = lex[word + "\t" + pos]
            if pos == "VERB" and "Part" in morph:
                lemma = lex[word + "\t" + pos]
            if pos in ["NOUN","ADJ"] and "Plur" in morph:
                lemma = lex[word + "\t" + pos]

    return lemma


def get_annos(morph):
    if morph == "_":
        return {}
    else:
        annos = morph.split("|")
        output = {}
        for anno in annos:
            k, v = anno.split("=")
            output[k] = v
    return output

gold_file = "C:\\Uni\\Corpora\\Hebrew\\IAHLT_HTB\\he_htb-ud-test.conllu"
pred_file = "he_htb-ud-test_pred.conllu"
#pred_file = "he_htb-ud-test_goldpos_pred.conllu"
#pred_file = "he_htb-ud-test_marmot_pred.conllu"

preds = []

metric = "acc"#"f1"
target = "lemma"#"morph"

print("Base: 0.9653150134048257")

for line in open(pred_file).read().split("\n"):
    if "\t" in line:
        fields = line.split("\t")
        if "-" in fields[0]:
            continue
        fields[2] = post_process(fields[1],fields[4],fields[2],fields[5])
        if target == "pos":
            preds.append(fields[4])
        elif target == "lemma":
            preds.append(fields[2])
        else:
            preds.append(fields[5])

gold = []
for line in open(gold_file).read().split("\n"):
    if "\t" in line:
        fields = line.split("\t")
        if "-" in fields[0]:
            continue
        if target == "pos":
            gold.append(fields[4])
        elif target == "lemma":
            gold.append(fields[2])
        else:
            gold.append(fields[5])
tok_count = len(gold)

if target == "morph":
    all_preds = defaultdict(lambda :defaultdict(lambda :"_"))
    all_golds = defaultdict(lambda :defaultdict(lambda :"_"))
    all_annos = set()
    for i, g in enumerate(gold):
        anno_kv = get_annos(g)
        for anno, val in anno_kv.items():
            all_golds[i][anno] = val
            all_annos.add(anno)
        anno_kv = get_annos(preds[i])
        for anno, val in anno_kv.items():
            all_preds[i][anno] = val
            all_annos.add(anno)

    for anno in sorted(list(all_annos)):
        if metric=="acc":
            golds = [all_golds[i][anno] for i in range(tok_count)]
            preds = [all_preds[i][anno] for i in range(tok_count)]
            print(anno+"\t",end="")
            print(accuracy_score(golds, preds))
        else:
            golds = [all_golds[i][anno] for i in range(tok_count) if not (all_golds[i][anno] == "_" and all_preds[i][anno] == "_")]
            preds = [all_preds[i][anno] for i in range(tok_count) if not (all_golds[i][anno] == "_" and all_preds[i][anno] == "_")]
            labs = list(set([all_preds[i][anno] for i in all_preds]))
            print(anno+"\t",end="")
            print(f1_score(golds, preds,average="micro",labels=labs))


else:

    print(accuracy_score(gold,preds))
    errs = [str((g,preds[i])) for i, g in enumerate(gold) if preds[i] != g]
    print("\n".join(errs))
    print(len(errs))
    if target != "lemma":
        print(classification_report(gold,preds))