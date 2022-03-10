SHELL = /bin/bash

outDir = build
pkg = sodalite
mypy = ${activate} && mypy --config mypy.ini -p ${pkg} -p tests ${shell [ ${color} != 'true' ] && echo '--no-color-output'}
reportDir = ${outDir}/reports

activate = . venv/bin/activate



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


# logs are written to journald in order not to interfere with the TUI
logs:
	journalctl --identifier sodalite --follow
.PHONY: logs

venv: setup.py
	python -m venv venv
	${activate} && pip install '.[dev]'
	@touch venv

deps: venv
.PHONY: deps

check: lint type-check test
.PHONY: check

test: venv
	${activate} && pytest tests
.PHONY: test

lint: venv
	${activate} && flake8 ${pkg} tests
.PHONY: lint

prune: clean
	rm -rf venv
.PHONY: prune

clean:
	rm -rf db.sqlite ${outDir} sodalite.egg-info
.PHONY: clean

build: venv
	${activate} && python setup.py build
.PHONY: build

setup-hooks:
	@for file in scripts/hooks/*; do \
		ln -sf ../../$$file .git/hooks/$$(basename $$file); \
		echo Symlinked git hook: $$(basename $$file); \
	done


import-profile: deps
	${activate} \
	&& pip install tuna \
	&& tuna <(python -X importtime -m sodalite 2>&1 1>/dev/null)
.PHONY: import-profile

###################
#### Installer

root =
prefix = /usr
root_prefix = ${root}${prefix}
docs = ${root_prefix}/share/doc/sodalite
share = ${root_prefix}/share/sodalite
man1 = ${root_prefix}/share/man/man1

install = install

test-metadata:
	desktop-file-validate meta/de.hnicke.Sodalite.desktop
	appstream-util validate meta/de.hnicke.Sodalite.appdata.xml

install-misc:
	${install} -Dm755 {scripts,${root_prefix}/bin}/sodalite-open
	${install} -Dm644 {meta,${root_prefix}/share/applications}/de.hnicke.Sodalite.desktop
	${install} -Dm644 {meta,${root_prefix}/share/metainfo}/de.hnicke.Sodalite.appdata.xml
	${install} -Dm644 {docs,${man1}}/sodalite.1
	${install} -Dm644 {docs,${man1}}/sodalite-open.1
	${install} -Dm644 {.,${docs}}/README.md
	${install} -Dm644 {.,${docs}}/copyright
	${install} -Dm644 {.,${docs}}/CHANGELOG.md
	${install} -Dm644 {scripts,${share}}/shell-integration.sh
	${install} -Dm644 {scripts,${share}}/shell-integration.fish
	${install} -Dm644 {sodalite/core,${share}}/sodalite.conf
.PHONY: install-misc

