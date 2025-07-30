tags = {"NOUN","VERB","ADJ","ADV","PROPN"}

lex = open("C:\\Uni\\Hebrew\\HebPipe.git\\hebpipe\\data\\heb.lex",encoding="utf8").read().strip().split("\n")
lex = [l for l in lex if "\t" in l]
lex = [l for l in lex if l.split("\t")[1] in tags]

with open("heb.lemma",'w',encoding="utf8",newline="\n") as f:
    f.write("\n".join(sorted(lex)))