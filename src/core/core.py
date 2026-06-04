"""

AOPM core (src/core/core.py)
----------
Description: Main script, check, prepare and execute all the other modules in AOPM
Made by: GusDev
Version: 1.0.0

"""

# imports
import sys
import subprocess as sub
import importlib.util
import os
from configparser import ConfigParser

from tqdm import tqdm
from pathlib import Path as p
from tempfile import TemporaryDirectory

# try import API
try:
	from aopmAPI import *
	success("aopmAPI imported!")
except:
	print("Cant import aopmAPI :(")
	sys.exit(1)

"""
 #####################
## GLOBAL VARIABLES ##
#####################
"""
configPath = "/home/gustavo/PycharmProjects/aopm/config/aopm.cfg"
printedLines = 0

"""
 ##############
## FUNCTIONS ##
##############
"""

def load_module(module_path: str):
	"""
	Import a module, init and then return it

	:param module_path:
	:return:
	"""
	spec = importlib.util.spec_from_file_location("module", module_path)

	if spec is None:
		error(f"Cant create the spec for: '{module_path}' :( Something went wrong btw", True, 1)

	module = importlib.util.module_from_spec(spec)

	sys.modules["module"] = module

	if spec.loader is None:
		error(f"Cant load the module in path: '{module_path}' :( Something went wrong btw", True, 1)

	spec.loader.exec_module(module)
	return module


"""
 ###############
## CORE FLAGS ##
###############
"""
selfClear = False
ignoreGpgChecks = False
verbose = False

"""
 ##############
## MAIN LOOP ##
##############
"""
# basic arguments wrappers
argv = sys.argv
argc = len(argv)

# check if user is root
if os.geteuid() != 0:
	error("To use AOPM you must be root! or just 'sudo' >:)", True, 1)

# check if it has 1 or more arguments
if argc < 1:
	error("Too few arguments :( Try use 'aopm help me' :)", True, 1)

# open the config file
cfg = ConfigParser()
cfg.read(configPath)

# make basic checks
essentialSections = ["paths", "security"]
essentialOptions = [
	{"paths": "modules_path"},
	{"paths": "modules_keys_path"},
	{"paths": "modules_sigs_path"},
	{"security": "expected_modules_fingerprints"}
]

target("Check config file...")
printedLines += 1
for section in essentialSections:
	if not cfg.has_section(section):
		error(f"The config file dont have the '{section}' section! Please repair it or re-create the config file :)", True, 1)

for option in essentialOptions:
	for section, opt in option.items():
		if not cfg.has_option(section, opt):
			error(f"The config file dont have the '{opt}' option in '{section}' section! Please repair it or re-create the config file :)", True, 1)

success("Config file checked!")
printedLines += 1

target("Define global variables...")
printedLines += 1

modulesPath = cfg.get("paths", "modules_path")
modulesKeyPath = cfg.get("paths", "modules_keys_path")
modulesSigsPath = cfg.get("paths", "modules_sigs_path")
expectedModulesFingerprints = cfg.get("security", "expected_modules_fingerprints").strip().split()

if verbose:
	success("Global variables defined!")
	printedLines += 1

# parse the arguments
coreArgs = []
moduleArgs = []
for arg in argv[1:]:
	if arg.startswith("---"):
		coreArgs.append(arg)
	else:
		moduleArgs.append(arg)


# treat the core arguments
for arg in coreArgs:
	# strip and remove the '---' prefix
	match arg.strip().split("---")[1]:
		case "self-clear":
			selfClear = True
		case "ignore-gpg-checks":
			ignoreGpgChecks = True
		case "verbose":
			verbose = True
		case _:
			error(f"Unknown core argument: '{arg}'! Try use 'aopm flags core' for more info :)", True, 1)

target("Find module to open...")
printedLines += 1
print("-" * 30)
printedLines += 1
bar = tqdm(total=100, desc=f"Trying to find modules directory")
printedLines += 1
if p(modulesPath).is_dir():
	bar.update(40)
	bar.desc = f"Trying to find module: '{moduleArgs[0]}'"
else:
	bar.close()
	error(f"Cant found the modules_path ('{modulesPath}) :( Try change the 'modules_path' in your config file :)", True, 1)

if p(f"{modulesPath}/{moduleArgs[0]}.py").is_file():
	bar.update(50)
else:
	bar.close()
	error(f"Cant found the module: '{moduleArgs[0]}' :( Try change the 'modules_path' in your config file :)", True, 1)

if p(modulesSigsPath).is_dir():
	bar.update(5)
else:
	bar.close()
	error(f"Cant found the modules_sigs_path ('{modulesSigsPath}') :( Try change the 'module_sigs_path' in your config file :)", True, 1)

if p(modulesKeyPath).is_dir():
	bar.update(5)
else:
	bar.close()
	error(f"Cant found the modules_key_path ('{modulesKeyPath}') :( Try change the 'modules_key_path' in your config file :)", True, 1)

bar.close()
print("-" * 30)
printedLines += 1
if verbose:
	success(f"Module: '{moduleArgs[0]}' found!")
	printedLines += 1

if not ignoreGpgChecks:
	target("Check module GPG sig")
	printedLines += 1
	with TemporaryDirectory() as tmp:
		if verbose:
			success(f"Temporary directory created! '{tmp}'")
			target("init the GPG checker")
			printedLines += 2
		gpg = GPGChecker(tmp)
		target("Import the GPG keys")
		printedLines += 1
		for item in p(modulesKeyPath).iterdir():
			if item.is_file():
				gpg.import_key(str(item), True)
			else:
				warn(f"Directory '{item}' found in the modules key directory :/")
		if verbose:
			success("GPG keys imported!")
			target("Find the .sig file")
			printedLines += 2
		if p(f"{modulesSigsPath}/{moduleArgs[0]}.sig").is_file():
			success(".sig file found!")
			printedLines += 1
		else:
			error("Cant found the .sig file in modules sigs directory :( Check if it has all the .sig's files, or use '---ignore-gpg-checks' :)", True, 1)
		result = gpg.verify_file(f"{modulesPath}/{moduleArgs[0]}.py", f"{modulesSigsPath}/{moduleArgs[0]}.sig")
		verified = False
		for fp in expectedModulesFingerprints:
			if result.fingerprint == fp:
				verified = True

			if verified:
				break
		if verified:
			if verbose:
				success("The module passed in the GPG check!")
				printedLines += 1
		else:
			error("The file dont passed on the GPG check! With you want ignore that, use '---ignore-gpg-checks' at your own risk!", True, 1)
else:
	warn("The module GPG check was skipped by the flag: '---ignore-gpg-checks' :/ Continue at your own risk!")

success("GPG check done!")
printedLines += 1
target("Check module functions")
printedLines += 1

module = load_module(f"{modulesPath}/{moduleArgs[0]}.py")
