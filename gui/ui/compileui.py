#/usr/bin/env python
# -*- coding: utf-8 -*-

import os

path = os.getcwd()
prefix = "Ui_"

def compile(uicfile):
	file = prefix+ os.path.splitext(uicfile)[0] + ".py"
	file_c = file + "c"
	print(" * Compiling "+uicfile+" to "+file)
	if os.path.isfile(file):
		print("   Deleting existing "+file)
		os.remove(file)
	if os.path.isfile(file_c):
		print("   Deleting existing "+file_c)
		os.remove(file_c)
	errlevel = os.system("pyuic4 -o " + file + " " + uicfile)
	if errlevel != 0:
		print("   Error compiling " + uicfile + ". Aborting.")
		sys.exit(-1)

print("Compiling Qt4 UI files in folder " + path)
for subdir, dirs, files in os.walk(path):
	for file in files:
		if file.endswith(".ui"):
			compile(file)
print("All files compiled.")