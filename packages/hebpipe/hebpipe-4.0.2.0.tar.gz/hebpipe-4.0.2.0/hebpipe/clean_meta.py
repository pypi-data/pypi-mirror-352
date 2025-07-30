import os, sys, re

lines = open("wiki_corpus.conllu",encoding="utf8").read().split("\n")

output = []
meta = []
sid = 1
for line in lines:
    if line.startswith("#"):
        if "newdoc_id" in line:
            line = line.replace("newdoc_id","newdoc id")
            output.append(line)
            continue
        elif line.startswith("#"):
            if "= NULL" in line:
                line = line.replace("= NULL","")
            line = line.strip().replace("&quot;",'"').replace("&amp;","&").replace("&gt;",">").replace("&lt;","<")
            meta.append(line)
    elif line.startswith("1\t") or line.startswith("1-"):
        if len(meta)>0:
            meta = ["# sent_id = wiki_corpus-" + str(sid)] + meta
            output += sorted(meta)
            sid += 1
            meta = []
        output.append(line)
    else:
        output.append(line)

with open("wiki_corpus_clean.conllu",'w',encoding="utf8",newline="\n") as f:
    f.write("\n".join(output).strip() + "\n\n")