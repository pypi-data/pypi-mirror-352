import sys, io, re, os
from argparse import ArgumentParser
from f_score_segs import main as f_score
from collections import defaultdict
from six import iterkeys

PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep

lex = script_dir + ".." + os.sep + "data" + os.sep + "copt_lemma_lex_cplx_2.5.tab"
frq = script_dir + ".." + os.sep + "data" + os.sep + "cop_freqs.tab"
conf = script_dir + ".." + os.sep + "data" + os.sep + "test.conf"
ambig = script_dir + ".." + os.sep + "data" + os.sep + "ambig.tab"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from tokenize_rf import RFTokenizer
from stacked_tokenizer import StackedTokenizer


def tt2seg_table(tt_string,group_attr="norm_group",unit_attr="norm"):

	group = ""
	output = ""
	units = []
	pairs = []
	for line in tt_string.split("\n"):
		if " " + group_attr + "=" in line:  # new group
			group = re.search(" " + group_attr + '="([^"]+)"',line).group(1)
		if "</" + group_attr +">" in line:
			pairs.append((group,"|".join(units)))
			group = ""
			units = []
		if " " + unit_attr + "=" in line:  # new unit
			unit = re.search(" " + unit_attr + '="([^"]+)"',line).group(1)
			units.append(unit)

	for grp, segs in pairs:
		output += grp + "\t" + segs + "\n"

	return output


p = ArgumentParser()
p.add_argument("--train_list",default="train_list.tab",help="file with one file name per line of TT SGML training files")
p.add_argument("--test_list",default="test_list.tab",help="file with one file name per line of TT SGML test files")

opts = p.parse_args()

train_list = io.open(opts.train_list,encoding="utf8").read().strip().split("\n")
test_list = io.open(opts.test_list,encoding="utf8").read().strip().split("\n")

train = ""
for file_ in train_list:
	tt_sgml = io.open(script_dir + file_,encoding="utf8").read()
	train += tt2seg_table(tt_sgml)

test = ""
for file_ in test_list:
	tt_sgml = io.open(script_dir + file_,encoding="utf8").read()
	test += tt2seg_table(tt_sgml)

# Remove bug rows
clean_test = []
for line in test.strip().split("\n"):
	grp, seg = line.split("\t")
	if len(grp) == len(seg.replace("|","")):
		clean_test.append(line)
test = "\n".join(clean_test)


rf = RFTokenizer(model="test")
if not PY3:
	train = unicode(train)


#io_file = io.StringIO()
#io_file.write(train)
#io_file.flush()
#io_file.close()

with io.open("_tmp_train.tab",'w', encoding="utf8") as f:
	f.write(train)

with io.open("_tmp_test.tab",'w', encoding="utf8") as f:
	f.write(test)

test_input = ""
for line in test.strip().split("\n"):
	test_input += line.split("\t")[0] + "\n"

golds = test.split("\n")

retrain=False
if retrain:
	rf.train("_tmp_train.tab",lexicon_file=lex,freq_file=frq,test_prop=0,dump_model=True,output_errors=True,conf=conf)
	preds = rf.rf_tokenize(test_input.strip().split("\n"))
	f_score("_tmp_test.tab","\n".join(preds),preds_as_string=True,ignore_diff_len=True)


stk = StackedTokenizer(no_morphs=True,model="test",pipes=True)
stk.load_ambig(ambig_table=ambig)

preds = stk.analyze("_".join(test_input.strip().split("\n")))
preds = preds.split("_")


f_score("_tmp_test.tab","\n".join(preds),preds_as_string=True,ignore_diff_len=True)

errs = defaultdict(int)
for i, pred in enumerate(preds):
	gold = golds[i].split("\t")[1]
	if pred != gold:
		errs[gold + "\t"+ pred] += 1

with io.open("errs.tab",'w',encoding="utf8") as f:
	for key in sorted(iterkeys(errs),reverse=True):
		f.write(key + "\t" + str(errs[key]) + "\n")