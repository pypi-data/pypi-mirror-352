import sys, io, os, re, tempfile, subprocess
from depedit import DepEdit

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
bin_dir = script_dir + ".." + os.sep + "bin" + os.sep
data_dir = script_dir + ".." + os.sep + "data" + os.sep
parser_path = bin_dir + "maltparser-1.8" + os.sep

PY3 = sys.version_info[0] == 3


def exec_via_temp(input_text, command_params, workdir=""):
	temp = tempfile.NamedTemporaryFile(delete=False)
	exec_out = ""
	try:
		temp.write(input_text.encode("utf8"))
		temp.close()

		command_params = [x if x != 'tempfilename' else temp.name for x in command_params]
		if workdir == "":
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
			(stdout, stderr) = proc.communicate()
		else:
			proc = subprocess.Popen(command_params, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,cwd=workdir)
			(stdout, stderr) = proc.communicate()

		exec_out = stdout
	except Exception as e:
		print(e)
	finally:
		os.remove(temp.name)
		if PY3:
			exec_out = exec_out.decode("utf8")
		return exec_out


d = DepEdit(config_file=data_dir + "add_ud_and_flat_morph.ini",options=type('', (), {"quiet":True,"kill":"both"})())

dev = io.open(data_dir + "cop_scriptorium-ud-dev.conllu",encoding="utf8").read()
train = io.open(data_dir + "cop_scriptorium-ud-train.conllu",encoding="utf8").read()
train += dev
train = train.split("\n")
train = d.run_depedit(train)

test_gold = io.open(data_dir + "cop_scriptorium-ud-test.conllu",encoding="utf8").read()
# Remove supertokens and comments with empty-rule depedit
d = DepEdit(options=type('', (), {"quiet":True,"kill":"both"})())
test_gold = d.run_depedit(test_gold.split("\n"))
test_gold = test_gold.split("\n")


test_blank = []
for line in test_gold:
	if "\t" in line:
		fields = line.split("\t")
		fields[6:] = ["_","_","_","_"]
	test_blank.append(line)

test_blank = d.run_depedit(test_blank)

cmd = ["java","-jar","maltparser-1.8.jar","-c","eval","-i","tempfilename",
	   "-F",r"C:\Uni\Coptic\git\corpora\treebank-dev\v2.1parser\addMergPOSTAGS0FORMStack0.xml",
	   "-m","learn","-grl","root","-pcr","none","-a","nivrestandard","-pp","head","-nr",
	   "true","-ne","false"]

# Train the parser
exec_via_temp(train,cmd,parser_path)

# Test
cmd = ['java','-mx512m','-jar',"maltparser-1.8.jar",'-c','eval','-i','tempfilename','-m','parse']
parsed = exec_via_temp(test_blank,cmd,parser_path)
parsed = parsed.replace("\r","")

total=0
correct_head=0
correct_label=0
correct_both=0
for i, line in enumerate(parsed.split("\n")):
	gold_line = test_gold[i]
	if "\t" in line:
		total +=1
		pred = line.split("\t")
		gold = gold_line.split("\t")
		if gold[6] == pred[6] or (pred[7] == "punct" and gold[7] == "punct"):
			correct_head+=1
		if gold[7] == pred[7]:
			correct_label+=1
		if gold[6:8] == pred[6:8] or (pred[7] == "punct" and gold[7] == "punct"):
			correct_both+=1

total = float(total)
print("Label accuracy: " + str(correct_label/total))
print("Attach accuracy: " + str(correct_head/total))
print("LAS: " + str(correct_both/total))
