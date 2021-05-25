
STUDENT_DIR?= student
MOVE?=mv
RMDIR?=rmdir

GITROOT:=$(shell git rev-parse --show-toplevel)

define copy_files
	@echo creating/cleaning ${1}
	if [ -n "${2}" ] ; then \
	  cp -a ${2} ${1}; \
	fi
endef


define cut_files
	if [ -n "${2}" ] ; then \
	for f in $2; do \
	  echo Cutting file $$f into $1/$$f ;\
	  sed -e '/START_CUT/,/END_CUT/{d;}' -e '/START_ADD/,/END_ADD/ {s/^\( *\)\(#\|\/\/\) /\1/g}' -e '/START_ADD/ {d}; /END_ADD/ {d}' $$f > $1/$$f ;\
	  if [ -x "$$f" ] ; then \
	    chmod +x $1/$$f; \
	  fi \
	done \
	fi
endef

student:
	test -n "$(TARGETDIR)"  # testing $$TARGETDIR
	test -n "$(PROGLANG)"   # testing $$PROGLANG (C or PY)
	rm -rf ${TARGETDIR}
	mkdir -p ${TARGETDIR}
	@for d in ${SUBDIRS} ; do \
	  $(MAKE) -C $$d student TARGETDIR=../${TARGETDIR}/$$d; \
	  rmdir --ignore-fail-on-non-empty ${TARGETDIR}/$$d; \
	done
	$(call copy_files,${TARGETDIR},${STUDENT_FILES_NOCUT})
	$(call copy_files,${TARGETDIR},${STUDENT_FILES_NOCUT_${PROGLANG}})
	$(call cut_files,${TARGETDIR},${STUDENT_FILES})
	$(call cut_files,${TARGETDIR},${STUDENT_FILES_${PROGLANG}})

student-py:
	rm -rf $@
	$(MAKE) student TARGETDIR=$@ PROGLANG=PY

student-c:
	rm -rf $@
	$(MAKE) student TARGETDIR=$@ PROGLANG=C

all-student: student-py student-c

clean-student:
	rm -rf student-py student-c

clean-all:
	@for d in ${SUBDIRS} ; do \
	  $(MAKE) -C $$d clean ; \
	done

TURINGDIR=../Turing/301_INF_Public

TURINGDIR-C=${TURINGDIR}/APP_C
TURINGDIR-PY=${TURINGDIR}/APP_Python


APPDIR=$(shell basename $(CURDIR))
APPNUM=$(shell echo ${APPDIR} | sed -e 's/-.*//')

APPTURDIR-C=${TURINGDIR-C}/${APPNUM}
APPTURDIR-PY=${TURINGDIR-PY}/${APPNUM}

define generic_turing
	@echo creating/cleaning $2
	mkdir -p ${2}
	rm -rf ${2}/*
	@echo moving student content
	mv ${1}/* ${2}
	rmdir ${1}
	@echo setting permissions
	chmod -R g+rwX  ${2}
	chmod -R o+rX   ${2}
	@echo ""
	@echo "***********************************"
	@echo Done: please synch with turing now!
	@echo "***********************************"
	@echo ""
endef

turing-c: student-c
	$(call generic_turing,student-c,${APPTURDIR-C})

turing-py: student-py
	$(call generic_turing,student-py,${APPTURDIR-PY})



# Warning: mettre simplement turing-c et turing-py
# comme dépendence ne fonctionne pas, car la cible
# 'student' n'est construite qu'une fois et on perd
# les copies des fichiers communs
turing:
	$(MAKE) turing-c
	$(MAKE) turing-py

# WEBDOWNLOAD=sncf:~/AppoStar/AppoWeb/static/download/
WEBDOWNLOAD=${GITROOT}/public/download/Code-APPs/

define generic_zip
	cd ${1}; \
	  ls; \
	  zip -r ${APPNUM}-${2}.zip ${APPNUM}; \
	  mv -f ${APPNUM}-${2}.zip ${WEBDOWNLOAD}
endef
# old on appolab
# scp ${APPNUM}-${2}.zip ${WEBDOWNLOAD}


zip-upload:
	@echo make sure turing files are up-to-date
	@echo before zipping them
	$(call generic_zip,${TURINGDIR-C},C)
	$(call generic_zip,${TURINGDIR-PY},Python)
	@echo Now commit new zip files in git and push


.PHONY: student all-student student-c student-py turing turing-c turing-py zip

# testturing:
# $(call generic_turing,hello)

