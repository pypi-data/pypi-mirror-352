# Cyda
Cyda is a *much* simpler build system for C/C++. Designed after feeling lazy to write Makefiles for each new project. 

Whenever I started a new project in C/C++, I would always manually create folders to organize my code and then finally, create the Makefile. 
Here is what my makefile would *generally* look like at the start of a brand new project
```make
CC = gcc
CFLAGS = -Wall -Ilib
OBJ = lib/lib1.o lib/lib2.o
TARGET = main

all: $(TARGET)

$(TARGET): $(OBJ) src/main.o
	$(CC) -o $@ $^

lib/lib1.o: lib/lib1.c lib/lib1.h
	$(CC) $(CFLAGS) -c $< -o $@

lib/lib2.o: lib/lib2.c lib/lib2.h
	$(CC) $(CFLAGS) -c $< -o $@

src/main.o: src/main.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f lib/*.o src/*.o $(TARGET)
```
Multiple symbols like $<, $@, $^, etc. Although some of you may say 'just learn it, you'll get used to it', but *i was lazy.*

Here is what my *cydafile* looks like in new projects now:
```
compiler gcc
flags -Wall
// include lib => -Ilib
include lib
// Target main
exec main

// You'll notice that the header file for the c files are not given, cyda assumes that lib1.c has a coresponding lib1.h since its standard
file lib/lib1.c
file lib/lib2.c
file src/main.c
// This is like ~50% smaller than the makefile at the start of this readme!
```
Aaand you're done! 
No rules needed for .o, or cleaning the .o files later

`--new <project name> -c/c++/cxx/cpp --compiler gcc/clang/g++/clang++` is the concept I borrowed from cargo, because once again, I was quite tired of setting up manually my folder structure. It automatically creates a new folder named `<project name>` with starter files for `C/C++` according to the flag and then optionally, you can specify the compiler. 
The folder structure it generates is quite standard --
```
PROJECT_NAME
  | --- libs/
  |       | --- lib1.c  / or lib1.cpp
  |       | --- lib1.h
  |
  | --- src/
  |       | --- main.c  / or main.cpp 
  |
  | --- cydafile
```
And the cydafile generated matches the folder structure already. 

Cyda Syntax: `use --syntax to learn as well ;)`

1. compiler <compiler name>
   Select the desired compiler. Permitted values are gcc, g++, clang, clang++. You can choose a different compiler and override later, if you'd like.
   It'll just prompt you when you run the file, if you decide to choose a different compiler

2. flags <compiler flags>
   Set the desired flags for the compiler. This is compiler dependant
   Here lies stuff like -Wall, -O3, etc

3. include <paths/dirs to include in compilation>
    - This corresponds to -I flag in gcc/clang, ignore if your compiler doesnt support it

4. library <library to include>
    - This corresponds to -l flag in gcc/clang, but if it isn't a system library, links with libraries in the 'explicit' path
  
    - For example, if using math.h, you would use library math to add it to the list of flags for your compiler to link against (-lm, in this case)
    - But, if have your own library called mystuff.a in, say, staticlibs/, you would use library staticlibs/mystuff
    - Do note that the two above commands, `include` and `library`, can be both set using `-I` and `-l` in the `flags` command as well, and you wouldn't need to add them to library/include and vice versa.

Here are the mappings for the library name to their `-l` equivalent:
{
	"math" 			: "m",
	"pthread" 		: "pthread",
	"dlopen" 		: "dl",
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

If you think that is inconvenient, you can just add your `-l` command in the `flags` 

5. file <filename, along with path>
    - This is the complete filename from the present working directory.
    - For example, if its in the present working directory, then main.c should suffice, else specify using src/main.c

6. set output obj <directory>
    - Determines where the generated object files will reside. 
    - For example, setting it to object_files will make it generate in ./object_files/*.o
    - There is no way to tweak the output directory/area for *each* file, I think thats unneccessary, atleast for me
    - By default, it generates object files in `./` 

7. set output exe <directory>
    - Determines where the generated executable will reside. 
    - For example setting it to dist will make it generate in ./dist/*
    - By default, it generates the executable in `./`

8. exec <name>
    - Set your program to be generate an executable. 
    - <name> is the name of the final executable.
    - That's about it

9.  slib <name>
    - Set your program to be generate a static library (.a). 
    - <name> is the name of the final library (<name>.a)

10.   dlib <name>
    - Set your program to be generate an dynamic library (.so). 
    - <name> is the name of the final library (<name>.so)

### There must be only one of 'exec', 'slib', or 'dlib'

And you're done! You know the basics of Cyda now! Have fun and I hope you find it easier than other build tools :p


## NOTE -
To add or suggest ideas/bugs/etc. you can contact the developer at `toodles.exe` on discord

May or may not add support for assembly (linux only)