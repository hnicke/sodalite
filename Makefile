APPNAME=sodalite

#SHELL=${/usr/bin/sh}
INSTALL=install
INSTALL_PROGRAM=${INSTALL}
INSTALL_DATA=${INSTALL} -m 644

prefix=/usr/local
exec_prefix=${prefix}
bindir=${exec_prefix}/bin
datarootdir=${prefix}/share
datadir=${datarootdir}
appdatadir=${datadir}/${APPNAME}
sysconfdir=${prefix}/etc
docdir=${datarootdir}/doc
appdocdir=${docdir}/${APPNAME}
libdir=${exec_prefix}/lib
applibdir=${libdir}/${APPNAME}
mandir=${datarootdir}/man
man1dir=${mandir}/man1
mimedir=${datadir}/applications
srcdir=.

configfile=${sysconfdir}/${APPNAME}.conf

all:

install: installdirs
	$(shell awk 'NR==1 {print; \
		print "DATA_DIR='"${appdatadir}"'"; \
		print "LIB_DIR='"${applibdir}"'"; \
		print "CONFIG_FILE='"${configfile}"'"} \
		NR!=1'  \
			${srcdir}/bin/${APPNAME} > ${DESTDIR}${bindir}/${APPNAME})
	chmod 755 ${DESTDIR}${bindir}/${APPNAME}

	${INSTALL_PROGRAM} ${srcdir}/bin/${APPNAME}-open ${DESTDIR}${bindir}
	@for file in $(shell cd ${srcdir}/${APPNAME}; find . -name '*.py'); do\
		${INSTALL_DATA} -D ${srcdir}/${APPNAME}/$$file ${DESTDIR}${applibdir}/${APPNAME}/$$file;\
	done
	${INSTALL_DATA} ${srcdir}/bin/shell-integration.sh bin/shell-integration.fish ${DESTDIR}${appdatadir}
	${INSTALL_DATA} ${srcdir}/${APPNAME}.desktop ${DESTDIR}${mimedir}
	${INSTALL_DATA} ${srcdir}/docs/${APPNAME}.1 ${DESTDIR}${man1dir}
	${INSTALL_DATA} ${srcdir}/docs/${APPNAME}-open.1 ${DESTDIR}${man1dir}
	gzip ${DESTDIR}${man1dir}/${APPNAME}.1
	gzip ${DESTDIR}${man1dir}/${APPNAME}-open.1
	${INSTALL_DATA} ${srcdir}/docs/${APPNAME}.conf ${DESTDIR}${configfile}
	${INSTALL_DATA} ${srcdir}/docs/${APPNAME}.conf ${DESTDIR}${appdatadir}
	${INSTALL_DATA} ${srcdir}/README.md ${DESTDIR}${appdocdir}/README
	${INSTALL_DATA} ${srcdir}/copyright ${DESTDIR}${appdocdir}
	${INSTALL_DATA} ${srcdir}/changelog.md ${DESTDIR}${appdocdir}/changelog


installdirs:
	${INSTALL} -d ${DESTDIR}${bindir} ${DESTDIR}${applibdir} ${DESTDIR}${appdatadir} \
		${DESTDIR}${appdocdir} ${DESTDIR}${man1dir} ${DESTDIR}${mimedir} ${DESTDIR}${sysconfdir}

uninstall:
	@rm -rfv ${applibdir}
	@rm -rfv ${appdocdir} 
	@rm -rfv ${appdatadir} 
	@rm -rfv ${mimedir}/${APPNAME}.desktop
	@rm -rfv ${man1dir}/${APPNAME}.1.gz
	@rm -rfv ${man1dir}/${APPNAME}-open.1.gz
	@rm -rfv ${bindir}/${APPNAME}
	@rm -rfv ${bindir}/${APPNAME}-open
	@rm -rfv ${configfile}


## ### PIPELINE / DEV TARGETS #####

activate = . venv/bin/activate
buildDir = build
pkg = sodalite
mypy = ${activate} && mypy --config mypy.ini -p ${pkg} -p tests ${shell [ ${color} != 'true' ] && echo '--no-color-output'}
reportDir = ${buildDir}/reports

venv: setup.py
	virtualenv venv -p $(shell which python3)
	${activate} && pip3 install '.[dev]'
	@touch venv

run: venv
	${activate} && bin/sodalite
.PHONY: run

check: lint type-check test
.PHONY: check

color = true
type-check ${reportDir}/index.txt ${reportDir}/index.html ${reportDir}/linecount.txt: venv ${pkg} tests
	${mypy} \
		--any-exprs-report ${reportDir} \
		--html-report ${reportDir} \
		--linecount-report ${reportDir} \
		--txt-report ${reportDir} 
.PHONY: type-check

type-report: ${reportDir}/index.txt
	cat ${reportDir}/index.txt
.PHONY: type-report

type-report-detail: ${reportDir}/index.html
	xdg-open $<
.PHONY: type-report-detail

# print percentage of type-coverage on line-basis
type-coverage: ${reportDir}/linecount.txt
	@cat $< | head -n1 | awk '{ \
		typed_lines = $$1; \
		total_lines = $$2; \
		typed_lines_percentage = (typed_lines / total_lines) * 100; \
		typed_functions = $$3; \
		total_functions = $$4; \
		typed_functions_percentage = (typed_functions / total_functions) * 100; \
		printf "%.2f\n", typed_lines_percentage; \
		#print "%.f\n", typed_functions_percentage; \
		}'
.PHONY: type-coverage

lint: venv
	${activate} && flake8 ${pkg} tests
.PHONY: lint


# logs are written to journald in order not to interfere with the TUI
logs:
	journalctl --identifier sodalite --follow
.PHONY: logs

test: venv
	${activate} && python3 -m pytest tests
.PHONY: test

e2e: venv
	docker build -f Dockerfile.e2e -t sodalite-e2e .
	docker run --rm -it sodalite-e2e
	#${activate} && python3 -m pytest --capture=no tests_e2e
.PHONY: e2e

prune: clean
	rm -rf venv
.PHONY: prune

clean:
	rm -rf db.sqlite ${buildDir}
.PHONY: clean

