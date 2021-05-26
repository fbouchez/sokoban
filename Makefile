all: main

# START_CUT
SUBDIRS=
STUDENT_FILES_PY= explore.py game.py graphics.py interface.py level.py player.py README.md scores.py
STUDENT_FILES_NOCUT= assets utils.py common.py Sokoban.py sounds.py

include students.mk

# END_CUT

CC=clang

## Flags de compilation en mode debug, convient pour presque tout l'APP
CFLAGS= -g -Wall -Wextra -Werror -Wno-unused-parameter

## Flags de compilation pour les test de performance.
## A decommenter pour desactiver tous les affichages
# CFLAGS=-O3 -g -Wall -Wextra -Werror -DSILENT -Wno-unused-parameter

# START_CUT
# CFLAGS=-g -Wall -Wextra #-DNCURSES #-Werror
LDFLAGS=-lncurses
# END_CUT


# Ici, on utilise l'"intelligence" de 'make' qui saura tout seul
# comment créer les .o à partir des .c
main: main.o curiosity.o listes.o interprete.o

# START_CUT


LOG=testlog.log

check-c: main
	./tests/check.sh c

check-py: main.py
	./tests/check.sh py

.PHONY: check-c check-py
# END_CUT

clean:
	rm -f main *.o
