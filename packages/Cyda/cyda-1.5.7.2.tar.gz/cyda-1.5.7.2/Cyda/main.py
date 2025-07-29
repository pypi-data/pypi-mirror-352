# Version 1.5.7

import shlex, sys, os
from time import time as stopwatch
import random
from pathlib import Path
import platform

PLATFORM_NAME = platform.system()
CYDAFILE_NAME = "cydafile"

# Some fun, totally motivating quotes for when the build fails
motivating_sentences = [
	"The disappointment of the gods is palpable",
	"Tsk tsk, Claude is coming",
	"Make it work or an LLM is gonna take your job",
	"I believe in you!",
	"GIT GUD",
	"........",
	"And you thought that would work?!?",
	"Remember that deadline? Yep, time to move it again.",
	"Remember that deadline? Yep, time to forget it.",
	"My LLM could write better code than that (I have no LLM)",
	"Forgot the semi-colon again? Sigh.",
	"Got a 19 page thesis summary of your template instantiation error? Sigh.",
	"Congratulations! Your code now fails in 3 architectures instead of 1.",
]
motivating_sentence = random.choice(motivating_sentences)

programmer_quotes = [
	["Debugging", "Anonymous"],
	["Software is like drugs, its better when its free", "Linus Torvalds (creator of Linux)"],
	["Programs must be written for people to read, and only incidentally for machines to execute", "Harold Abelson"],
	["The most damaging phrase in the language is, 'it's always been done this way'.", "Grace Hopper"],
	["Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live.", "John Woods"],
	["A poor programmer blames the language, a good programmer blames the compiler.", "Alan Perlis"],
	["Software and cathedrals are much the same — first we build them, then we pray.", "Anonymous"],
	["A clever person solves a problem. A wise person avoids it.", "Anonymous"],
	["The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie (creator of C)"],
	["Everybody should learn to program a computer because it teaches you how to think.", "Steve Jobs (founder of Apple)"],
	["The three great virtues of a programmer: laziness, impatience, and hubris.", "Larry Wall (inventor of Perl)"],
	["Some people, when confronted with a problem, think 'I know, I'll use regular expressions.' Now they have two problems.", "Jamie Zawinski (early Netscape dev)"],
	["When in doubt, use brute force", "Ken Thompson (co-creator of Unix)"],
	["Real programmers don't comment their code. If it was hard to write, it should be hard to understand.", "Ed Post"],
]
programmer_quote = random.choice(programmer_quotes)

class Cydafile:
	def __init__(self, compiler:str, flags:str, files:list[str], include_paths:list[str], executable_name:str, output_obj:str, output_exe:str, is_static_lib:bool, is_dynamic_lib:bool, libraries:str):
		self.compiler = compiler
		self.flags = flags
		self.files = files           			# Although named .files, its actually the filepaths, because explicit specification of the files are done :D
		self.include_paths = include_paths
		self.executable_name = executable_name
		self.output_obj = output_obj
		self.output_exe = output_exe
		self.is_slib = is_static_lib
		self.is_dlib = is_dynamic_lib
		self.libraries = libraries

def red(str):
	return f"\x1b[31m{str}\x1b[0m"

def green(str):
	return f"\x1b[32m{str}\x1b[0m"

def yellow(str):
	return f"\x1b[33m{str}\x1b[0m"

def errprint(*things) -> None:
	for thing in things:
		print(red(thing), end=' ')
	print()

def okprint(*things) -> None:
	for thing in things:
		print(green(thing), end=' ')
	print()

def infoprint(*things) -> None:
	for thing in things:
		print(yellow(thing), end=' ')
	print()

def extract_filename_from_path(path:str) -> str:
	fn = path.split(".")[0]
	fn = fn.split("/")
	fn = fn[len(fn) - 1]
	return fn

known_libraries = {
	# e.g:
	# math --> -lm
	"math" 			: "m",
	# pthread --> -lpthread
	"pthread" 		: "pthread",
	# dlopen  --> -ldl
	"dlopen" 		: "dl",
	# ...
	"dlsym"		    : "dl",
	"ncurses" 		: "ncurses",
	"readline"	    : "readline",
	"zlib" 			: "z",
	"ssl" 			: "ssl",
	"crypto"		: "crypto",
	"sqlite3" 		: "sqlite3",
	"curl"			: "curl",
	"X11" 			: "X11",
	"Xlib" 			: "X11",
	"Xorg" 			: "X11",
	"png" 			: "png",
	"jpeg"			: "jpeg",
	"gl" 			: "GL",
	"opengl"	    : "GL",
	"sdl"			: "SDL2",
	"sdl2" 			: "sdl2",
	"sndfile" 		: "sndfile",
	"uuid" 			: "uuid",
	"pcap" 			: "pcap",
	"pcapture" 		: "pcap",
	"gtk" 			: "gtk-3",
	"audio" 		: "ao",
	"ao" 			: "ao"
}

# Main function for parsing the cydafile itself
def read_cydafile() -> Cydafile:
	i = 1
	compiler = ""
	include_paths = []
	flags = ""
	executable_name = ""
	files = []
	output_obj = "."
	output_exe = "."
	is_static_lib = False
	is_dynamic_lib = False
	is_executable = False
	libraries = ""
	
	# global variable for the name of the file we want to read
	# set by the main() function, defaults to 'cydafile', otherwise set by the user explicitly
	global CYDAFILE_NAME
	if CYDAFILE_NAME in [f.strip().lower() for f in os.listdir(".")]:
		for line in open(f"./{CYDAFILE_NAME}", "r").readlines():
			command = shlex.split(line)
			if not len(command) > 0: continue   # if the command is empty, skip
			match command[0]:
				# Comments
				case "//":
					continue
				
				# setting compiler
				case "compiler":
					try:
						compiler = command[1]
					except:
						errprint(f"Error on line {i}. Compiler not specified. Exiting...")
						sys.exit(0)

				# 'set' command, currently used for setting output directories
				case "set":
					try:
						command2 = command[1] + " " + command[2]
					except:
						errprint(f"Error on line {i}. You didn't tell me *what* to set D: Exiting...")
						sys.exit(0)
					match command2:
						case "output obj":
							output_obj = command[3]
						case "output exe":
							output_exe = command[3]
				
				# 'include' for -I equivalent
				case "include":
					try:
						path = command[1]
					except:
						errprint(f"Error on line {i}. Did you forget to add a include path? Exiting...")
						sys.exit(0)
					include_paths.append(path)

				# 'flags' for, well, flags (for the compiler)
				case "flags":
					flags = " ".join([flag for flag in command[1:]])
				
				# adding files to the project compilation
				case "file":
					try:
						files.append(command[1])
					except:
						errprint(f"Error on line {i}. File name not specified. Exiting...")
						sys.exit(0)

				# 'library' for adding libraries, -l syntax for system libraries
				# and I figured its simpler just adding custom libraries using explicit path, instead of using -L.
				case "library":
					tmp = []
					cwd_libs = []
					final = ""
					
					# Disclaimer
					if PLATFORM_NAME == "Windows":
						errprint("Although not the case with every library, it is recommended you make sure that you have the required libraries")
						errprint(tmp)
						errprint("Because some libraries do not work out-of-the-box for Windows")
					
					# Get the libraries mentioned
					try:
						tmp = command[1:]
					except:
						errprint(f"Error on line {i}. No libraries specified to include. Exiting...")
						sys.exit(0)

					# Just format the comma separated libraries and append them to flags, cus they are flags.
					for lib in tmp:
						lib = lib.replace(',', '')
						# If its a known system library
						if lib in known_libraries:
							final += f" -l{known_libraries[lib]}"
						
						# If it isnt a known library, the user must explicitly specify the path
						# this is basically the same as adding it in the list of files to compile
						# but .c files get converted to .o, so these are explicitly libraries, not just any file
						elif os.path.exists(f"./{lib}.so"):
							libraries += f" ./{lib}.so"

						elif os.path.exists(f"./{lib}.a"):
							print(f"file was ./{lib}.a")
							libraries += f" ./{lib}.a"
						
						# It doesn't exist
						else:
							errprint(f"Error on line {i}. Either the library mentioned is not known by Cyda and/or doesn't exist in the path specified - '{lib}'")
							sys.exit(0)
					
					final += " "
					for lib in  cwd_libs:
						final += f" -l{lib}"
					flags += " " + final

				case "slib":
					# If we want to make a static library
					if is_dynamic_lib == True or is_executable == True:
						errprint(f"Error on line {i}. Already set to compile either as an executable or dynamic library. Can't set to static library. Exiting...")
						sys.exit(0)
					else:
						if is_dynamic_lib == True or executable_name != "":
							errprint("Error on line {i}. Either you already declared this as a dynamic library, or you named it as an executable. Decide on one :p Exiting...")
							sys.exit(0)
						try:
							executable_name = command[1]
							is_static_lib = True
						except:
							errprint(f"Error on line {i}. Executable name not specified. Exiting...")
							sys.exit(0)
					print("set static lib")
				
				case "dlib":
					if is_static_lib == True or is_executable == True:
						errprint(f"Error on line {i}. Already set to compile either as an executable or static library. Can't set to static library. Exiting...")
						sys.exit(0)
					else:
						if is_static_lib == True or executable_name != "":
							errprint("Error on line {i}. Either you already declared this as a static library, or you named it as an executable. Decide on one :p Exiting...")
							sys.exit(0)
						try:
							executable_name = command[1]
							is_dynamic_lib = True
						except:
							errprint(f"Error on line {i}. Executable name not specified. Exiting...")
							sys.exit(0)
				
				case "exec":
					if is_dynamic_lib == True or is_static_lib == True:
						errprint(f"Error on line {i}. Already set to compile either as an static or dynamic library. Can't set to static library. Exiting...")
						sys.exit(0)
					else:
						try:
							executable_name = command[1]
							is_executable = True
						except:
							errprint(f"Error on line {i}. Executable name not specified. Exiting...")
							sys.exit(0)
					
			i+=1

		if compiler == "":
			errprint("Compiler not set. Exiting...")
			sys.exit(0)
		if len(files) == 0:
			errprint("No files given. Exiting...")
			sys.exit(0)
		# Since we're setting the name of the executable in all three, static, dynamic, and executable
		# This is a shorter way of knowing if any of them were set at all
		if executable_name == "":
			errprint("No compilation type (static lib/dynamic lib/executable) not set. Exiting...")
			sys.exit(0)
	else:
		errprint("Uh, cydafile isn't found in this directory. Exiting...")
		sys.exit(0)
	
	return Cydafile(compiler, flags, files, include_paths, executable_name, output_obj, output_exe, is_static_lib, is_dynamic_lib, libraries)

def get_last_modified_exe(path:str):
	"""
	Given the path, gives you the last modified time of the executable
	Made into its own function because of platform dependant branches
	"""
	if PLATFORM_NAME == "Windows" and os.path.exists(f"./{path}.exe"):
		return os.path.getmtime(f"./{path}.exe")
	elif PLATFORM_NAME != "Windows" and os.path.exists(f"./{path}"):
		return os.path.getmtime(f"./{path}")
	else:
		# Doesn't exit
		return False
	

def compile_files(cyda:Cydafile, forced_recompile:bool) -> tuple[bool, list[str]]:
	"""
	
	If compilation succeeds, returns True
	else returns False

	Also returns list of obj files generated
	
	"""
	
	if cyda.compiler not in ["gcc", 'g++', 'clang', 'clang++']:
		i = input("I dont know the given compiler. Are you sure you want to proceed? (You can change the compiler later in the cydafile) [y/N]:")
		if i == "n" or not i:
			raise RuntimeError(red("Unrecognised compiler. Exiting..."))

	start = stopwatch()
	total = len(cyda.files)
	success = 0
	obj_files = []
	if cyda.output_obj != ".":
		Path(f"./{cyda.output_obj}/").mkdir(exist_ok=True)

	if cyda.output_exe != ".":
		Path(f"./{cyda.output_exe}/").mkdir(exist_ok=True)

	for filepath in cyda.files:
		fn = extract_filename_from_path(filepath)
		
		obj_files.append(f"{cyda.output_obj}/{fn}.o")
		try:
			mod_obj = os.path.getmtime(f"{cyda.output_obj}/{fn}.o")
		except FileNotFoundError as err:
			mod_obj = 0
		try:
			mod_c   = os.path.getmtime(filepath)
		except FileNotFoundError as err:
			errprint("[Fatal error] C file specified was not found, Exiting")
			raise RuntimeError("The C file could not be located while trying to check if a newer version exists.")

		if mod_c > mod_obj or forced_recompile == True:
			exit_code = os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} -c {filepath} {cyda.libraries} -o {cyda.output_obj}/{fn}.o")
			if exit_code == 0:
				success += 1
		else:
			total -= 1

	end = stopwatch()

	print("\n-------------------------------------------")
	print(f"DURATION: {round(end-start, 3)}s")
	if total == 0 and forced_recompile == False:
		infoprint("*** Nothing to do, already up to date object files. ***")
		return (True, obj_files)
	else:
		okprint(f"OK: {success}/{total}")
		print(red(f"FAIELD: {total-success}/{total}"))
		return (success == total, obj_files)


def need_recompile_executable(cyda) -> bool:
	"""
	
	Function that takes the Cyda file object and checks if any of the object files generated are *newer* than the present executable
	If the executable does not exist, or the object files are newer than the executable, returns true. 

	else returns false. (No need to recompile)

	"""
	final_exe_time = get_last_modified_exe(f"{cyda.output_exe}/{cyda.executable_name}/")
	if final_exe_time == False: # If it doesn't exist, then return true, because we need to generate the executable :p
		return True 

	for path in cyda.files:
		filename = extract_filename_from_path(path)
		mod_obj_time = os.path.getmtime(f"{cyda.output_obj}/{filename}.o")
		if mod_obj_time > final_exe_time:
			return True
		
	return False
		

def make_static_library(cyda:Cydafile):
	"""
	Makes a static binary at the desired location
	"""
	finalcmd = f"ar rcs {cyda.output_exe}/{cyda.executable_name}.a "

	for filepath in cyda.files:
		filename = extract_filename_from_path(filepath)
		os.system(f"gcc {cyda.flags} -c {filepath} -o {cyda.output_obj}/{filename}.o")
		finalcmd += f" {cyda.output_obj}/{filename}.o"

	if os.system(finalcmd) != 0:
		errprint(f"Encountered some error while creating the static binary.")
		sys.exit(1)
	else:
		okprint(f"Successfully created the static binary {cyda.output_exe}/{cyda.executable_name}.a")
		sys.exit(0)
	sys.exit(1)

def make_dynamic_library(cyda:Cydafile):
	"""
	Makes a dynamic binary at the desired location
	"""
	finalcmd = f"gcc -shared -o {cyda.output_exe}/{cyda.executable_name}.so "
	
	for filepath in cyda.files:
		filename = extract_filename_from_path(filepath)
		os.system(f"gcc {cyda.flags} -fPIC -c {filepath} -o {cyda.output_obj}/{filename}.o")
		finalcmd += f" {cyda.output_obj}/{filename}.o"

	if os.system(finalcmd) != 0:
		errprint(f"Encountered some error while creating the dynamic binary.")
		sys.exit(1)
	else:
		okprint(f"Successfully created the dynamic binary {cyda.output_exe}/{cyda.executable_name}.so")
		sys.exit(0)
	sys.exit(1)

def build(force_recompile:bool):
	"""
	
	The function that is called when --build is used
	
	"""
	cyda = read_cydafile()
	if cyda.is_slib: make_static_library(cyda)
	elif cyda.is_dlib: make_dynamic_library(cyda)
	result = compile_files(cyda, force_recompile)
	
	# Did compilation succeed?
	if result[0]:
		okprint(f"No failed compiles. Hurray!")
	else:
		print(red("FAILED IN COMPILING."))
		infoprint(motivating_sentence)
		sys.exit(0)

	# Do I need to recompile?
	if not need_recompile_executable(cyda) and force_recompile == False:
		infoprint("*** The executable is already up to date ***")
		infoprint("*** Nothing to do, exiting... ***")
		sys.exit(0)

	# Finally, if compilation succeeded and the obj files are newer than the executable, compile
	os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} {" ".join(result[1])} {cyda.libraries} -o {cyda.output_exe}/{cyda.executable_name}")
	print("-------------------------------------------\n")
	sys.exit(0)

def run(force_recompile:bool):
	"""
	
	The function that is called when --run is used
	
	"""
	cyda = read_cydafile()
	if cyda.is_slib or cyda.is_dlib: raise RuntimeError(red("Can't 'run' a static/dynamic library. Use --build. Exiting..."))
	result = compile_files(cyda, force_recompile)

	# Did compilation succeed?
	if result[0]:
		okprint(f"No failed compiles. Hurray!")
	else:
		errprint(f"FAILED IN COMPILING.")
		infoprint(motivating_sentence)
		# Exit if failure
		sys.exit(0)
	
	# Do I need to recompile?
	if not need_recompile_executable(cyda) and force_recompile == False:
		infoprint("*** The executable is already up to date ***")
		infoprint("*** Nothing to do, exiting... ***")
		sys.exit(0)

	# Finally, if compilation succeeded and the the obj files are newer than the executable, compile
	os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} {" ".join(result[1])} {cyda.libraries} -o {cyda.output_exe}/{cyda.executable_name}")
	print("-------------------------------------------\n")
	os.system(f"./{cyda.output_exe}/{cyda.executable_name}")
	sys.exit(0)

def clean():
	"""
	
	The function that is called when --clean is used

	"""
	cyda = read_cydafile()
	
	# If no output paths are specified, its the present working directory
	if cyda.output_obj != ".":
		Path(f"./{cyda.output_obj}/").mkdir(exist_ok=True)

	# "   "   "   "
	if cyda.output_exe == "": 
		cyda.output_exe = "."
	else: 
		Path(f"./{cyda.output_exe}/").mkdir(exist_ok=True)

	# For each file, go to the output directory for objects and delete that file
	for filepath in cyda.files:
		fn = extract_filename_from_path(filepath)
		os.system(f"rm -f ./{cyda.output_obj}/{fn}.o")

	# Platform dependant executable deletion
	if PLATFORM_NAME == "Windows":
		os.system(f"rm -f ./{cyda.output_exe}/{cyda.executable_name}.exe")
	else:
		os.system(f"rm -f ./{cyda.output_exe}/{cyda.executable_name}")
	sys.exit(0)
	
def generate_makefile():
	"""
	
	The function that is called when --makefile is used
	It does not support all functionality yet

	"""
	cyda = read_cydafile()
	# Disclaimer because some features aren't available, probably wont add them :p
	if cyda.output_obj != "" or cyda.output_exe != "":
		errprint("Please note that Cyda currently does not support generating makefiles that include")
		errprint("  - Custom object file output directories")
		errprint("	- Custom executable output directories")
		errprint("	- Wildcards for files")

	with open("Makefile", "w+") as file:
		file.truncate(0)
		
		# COMPILERS AND FLAGS
		file.writelines([
			f"CC = {cyda.compiler}\n",
			f"CFLAGS = {cyda.flags}\n",
			"\n",  
		])

		# FILE RULES
		for filepath in cyda.files:
			objfilename = extract_filename_from_path(filepath)
			file.write(f"\n{objfilename}.o: {filepath}\n	$(CC) $(CFLAGS) {' '.join(f'-I{d}' for d in cyda.include_paths)} -c {filepath} -o {objfilename}.o\n")
		file.write("\n")


		# FINAL EXECUTABLE RULE: LINE 1
		file.write(f"{cyda.executable_name}: ")   
		for filepath in cyda.files:
			objfilename = extract_filename_from_path(filepath)
			file.write(f"{objfilename}.o ")
			
		# COMPILE COMMANDS FOR FINAL EXECUTABLE RULE: LINE 2
		file.write("\n	$(CC) $(CFLAGS)")
		for filepath in cyda.files:
			objfilename = extract_filename_from_path(filepath)
			file.write(f"{objfilename}.o ")
			
		file.write(f"{' '.join(f'-I{d}' for d in cyda.include_paths)} -o {cyda.executable_name}\n")

		
		# CLEAN RULE
		file.write("clean: \n")
		file.write(f"	rm -f *.o {cyda.executable_name}\n")

		# RUN RULE
		file.write("run:\n")
		file.write(f"	make {cyda.executable_name}\n")
		
	okprint("If you see this message, your makefile is ready!")
	sys.exit(0)

def new_project(name, projtype, compiler_name):
	"""
	
	The function that is called when new projects are made. Supports C/C++ project types and gnu or clang compilers

	"""
	# If we dont recognise the filetype, error out. We don't deal with anything that isn't supported by cyda 
	if projtype not in ["-c", "-cpp", "-c++", "-cxx"]:
		raise RuntimeError(red(f"I don't know the specified project type {projtype} D:"))
	
	# If we dont recognise the compiler, just *ask* them once.
	if compiler_name not in ["gcc", 'g++', 'clang', 'clang++']:
		i = input("I dont know the given compiler. Are you sure you want to proceed? (You can change the compiler later in the cydafile) [y/N]:")
		if i == "n" or not i:
			raise RuntimeError(red("Unrecognised compiler. Exiting..."))
	
	# Create appropriate folders
	os.makedirs(f"./{name}/libs")
	os.makedirs(f"./{name}/src")

	# C programming language project
	if projtype == "-c":
		if compiler_name in ["g++", "clang++"]:
			errprint("Incompatible compiler for cxx used. Using fallback gcc")
		compiler_name = "gcc"
		
		with open(f"{name}/src/main.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				"\n",
				"int main(){\n"
				"	printf(\"Hello Cyda!\\n\");\n",
				"	hello_from_lib();\n"
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"\n",
				"void hello_from_lib(){\n"
				"	printf(\"Hi there!\\n\");\n"
				"}\n"
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				"\n",
				"void hello_from_lib();\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n",
				"include libs\n",
				"// This is also a flag, it sets -I\n",
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.c\n",
				"file libs/lib.c   // explicit path to be given\n",
				"set output obj objs_directory\n",
				"set output exe dist\n",
				f"exec {name}\n"
			])

	# C++ project type
	elif projtype in ["-cpp", "-c++", "-cxx"]:
		if compiler_name in ["gcc", "clang"]:
			errprint("Incompatible compiler for cxx used. Using fallback g++")
		
		compiler_name = "g++"
		with open(f"{name}/src/main.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				" \n",
				"int main(){\n"
				"	std::cout << \"Hello from Cyda!\" << std::endl;\n",
				"	std::cout << add_from_lib(3,5) << \"\\n\" << std::endl;\n",
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n",
				"\n",
				"int add_from_lib(int a, int b){\n",
				"	return a + b;\n",
				"}\n",
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				" \n",
				"int add_from_lib(int, int);\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall   \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n" 
				"include libs   ",
				"// This is also a flag, it sets -I\n"
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.cpp\n",
				"file libs/lib.cpp   // explicit path to be given\n",
				"set output obj objs_directory\n",
				"set output exe dist\n",
				f"exec {name}\n"
			])
	okprint(f"Project creation complete with name {name}!")
	sys.exit(0)
# lazy to write out "yellow", so
def y(s):
	return yellow(s)

def show_version_information():
	print("Currently running on version " + y("v1.5.7"))
	print("Recent additions include:")
	infoprint("    * Even further refactored code")
	print(f"    * Along with the previous version's {y("set output obj/exe")} commands, you can now use {y("libary")} command to link libraries using -l")
	print(f"        * if its not a recognised library by Cyda (which, if you'd like to add to, contact the dev! information on github) then Cyda looks for libraries within the pwd")
	print(f"        * also detects automatically if it was a .a or a .so, no need to specify the extension")
	print(f"    * Added {y("--force-recompile")} for {y("--run")}/{y("--build")} commands to, well, force recompile and ignores if previously built")
	print(f"    * Added support for generating {y("static")} libraries")
	print(f"    * Added support for generating {y("dynamic")} libraries")
	print(f"    * Another commandline utility added, {y("--quote")}")
	print(f"    * Added support for specifying {y("any file to be a cydafile (-f <name> or --from <name>)")}, but the default filename searched is still '{y("cydafile")}'")
	sys.exit(0)
	
def teach_syntax():
	infoprint("Quick, time to get you up and running with Cyda as soon as possible!")
	print(f"1. {y("compiler")} <compiler name>")
	print(f"    - Select the desired compiler. Permitted values are {y("gcc, g++, clang, clang++")}. You can choose a different compiler and {red("override")} later, if you'd like.")
	print()
	
	print(f"2. {y("flags")} <compiler flags>")
	print(f"    - Set the desired flags for the compiler. This is compiler dependant")
	print()
	
	print(f"3. {y("include")} <paths/dirs to include in compilation>")
	print(f"    - This corresponds to {y("-I")} flag in {y("gcc/clang")}, ignore if your compiler doesnt support it")
	print()
	
	print(f"4. {y("library")} <library to include>")
	print(f"    - This corresponds to {y("-l")} flag in {y("gcc/clang")}, but if it isn't a system library, links with libraries in the 'explicit' path")
	print(f"    - For example, if using math.h, you would use {y("library math")} to add it to the list of flags for your compiler to link against ({y("-lm")}, in this case)")
	print(f"    - But, if have your own library called {y("mystuff.a")} in, say, {y("staticlibs/")}, you would use {y("library staticlibs/mystuff")}")
	print(f"    - For the full list of which {y("libraries")} that correspond to what {y("-l")} tag, visit the Github page for the documentation")
	print(f"    - Do note that the two above commands, include and library, can be both set using {y("-I")} and {y("-l")} in the {y("flags")} command as well, and you wouldn't need to add them to library/include and vice versa.")
	print()
	
	print(f"5. {y("file")} <filename, along with path>")
	print(f"    - This is the complete filename from the present working directory. e.g if its in the pwd, then {y("main.c")} should suffice, else specify using {y("src/main.c")}")
	print()
	
	print(f"6. {y("set output obj")} <directory>")
	print(f"    - Determines where the generated {y("object")} files will reside. e.g setting it to {y("object_files")} will make it generate in ./{y("object_files")}/*.o")
	print()
	
	print(f"7. {y("set output exe")} <directory>")
	print(f"    - Determines where the generated {y("executable")} will reside. e.g setting it to {y("dist")} will make it generate in ./{y("dist")}/*")
	print()
	
	print(f"8. {y("exec")} <name>")
	print(f"    - Set your program to be generate an {y("executable")}. <name> is the name of the final executable")
	print()

	print(f"9. {y("slib")} <name>")
	print(f"    - Set your program to be generate a {y("static library (.a)")}. <name> is the name of the final library <name>.a")
	print()

	print(f"10. {y("dlib")} <name>")
	print(f"    - Set your program to be generate an {y("dynamic library (.so)")}. <name> is the name of the final library <name>.so")
	print()

	errprint("There must be only one of 'exec', 'slib', or 'dlib'\n")

	infoprint(f"And you're done! You know the basics of Cyda now! Have fun and I hope you find it easier than other build tools :p")
	print()
	sys.exit(0)

def show_help_information():
	infoprint("Welcome to using Cyda! A simpler CMake alternative.")
	print("Use " + y("--help")     + "  to get this message")
	print("Use " + y("--version")  + "  to, you know, get the installed version")
	print("Use " + y("--syntax")   + "  to get up to speed with the syntax of Cyda. Do visit the Github page for more information")
	print("Use " + y("--build")    + "  to build but not run the executable")
	print("Use " + y("--run")      + "  to build the files, clear the screen, and run the executable immediately")
	print("Use " + y("--clean")    + "  to clean the .o files generated")
	print("Use " + y("--new <project name>   -c/cpp   --compiler -gcc/g++/clang/clang++") + "  to create a new template project. use -c or -cpp/-cxx/-c++ to specify project language type.\n	   Optionally, specify the compiler using --compiler gcc/clang/clang++/g++/etc. By default cyda uses gcc/g++ :D\n")
	print("Use " + y("--makefile") + "  to generate a makefile for the given cyda script\n(Note: Some features like wildcards and setting output directories is not available for makefiles\n    It generates files in the current directory and searches paths explicitly\n    If you need those features, use --build/--run directly)\n")
	print("Use " + y("--force-recompile") + f"  along with --{y("run")} or --{y("build")} to force recompile and don't care if already built before\n")
	print("Use " + y("--quote")    + ", trust me")
	sys.exit(0)

def quoteprint(quote:list[str]):
	print(f"\"{quote[0]}\"")
	infoprint("                                   - " + quote[1])

def check_cydafile_exists():
	if not os.path.exists(f"./{CYDAFILE_NAME}"):
		infoprint(f"*** Well I didn't find the default cydafile, but here is a random quote from a famous programmer for you -\n")
		quoteprint(programmer_quote)
		print()
		okprint("* - If you are sure you have a cydafile in the pwd, but it isn't named cydafile, use -f <name>/--from <name>")
		sys.exit(1)
	infoprint(f"Running configuration from cydafile - '{CYDAFILE_NAME}'")

def main():
	global CYDAFILE_NAME
	commands = sys.argv[1:]

	if len(commands) == 0:	
		print("Use "+ y("--help") + " for, you guessed it, getting help.")
		sys.exit(1)

	if "-f" in commands:
		i = commands.index("-f")
		try:
			name = commands[i+1]
		except IndexError:
			errprint("Cydafile name not specified after -f. Exiting...")
			sys.exit(1)
		if os.path.exists(f"./{name}"):
			CYDAFILE_NAME = name
		else:
			errprint(f"Cydafile name not found ({name}). Exiting...")
			sys.exit(1)
	
	if "--from" in commands:
		i = commands.index("-f")
		try:
			name = commands[i+1]
		except IndexError:
			errprint("Cydafile name not specified after --from. Exiting...")
			sys.exit(1)
		if os.path.exists(f"./{name}"):
			CYDAFILE_NAME = name
		else:
			errprint(f"Cydafile name not found ({name}). Exiting...")
			sys.exit(1)
	
	if "--quote" in commands:
		quoteprint(programmer_quote)
		sys.exit(0)
	
	match commands[0]:
		case "--help":
			show_help_information()
		case "--version":
			show_version_information()
		case "--syntax":
			teach_syntax()
		case "--build":
			check_cydafile_exists()
			forced_recompile = False
			if len(commands[1:]) > 0 and commands[1] == "--force-recompile":
				forced_recompile = True
				infoprint("Running with force recompile.")
			build(forced_recompile)
		case "--run":
			check_cydafile_exists()
			forced_recompile = False
			if len(commands[1:]) > 0 and commands[1] == "--force-recompile":
				forced_recompile = True
				infoprint("Running with force recompile.")
			run(forced_recompile)
		case "--clean":
			check_cydafile_exists()
			clean()
		case "--makefile":
			check_cydafile_exists()
			generate_makefile()
		case "--new":
			try:
				name = commands[1]
			except:
				errprint("Name of project not specified. Exiting...")
				sys.exit(1)
			try:
				_type = commands[2]
			except:
				errprint("Project type (C/C++) not specified. Exiting...")
				sys.exit(1)
			
			try:
				compiler_name = commands[3]
				if compiler_name not in ["gcc", "g++", "clang", "clang++"]:
					raise RuntimeError()
			except:
				if _type == "-c":
					compiler_name = "gcc"
				else:
					compiler_name = "g++"

			new_project(name, _type, compiler_name)


main()
