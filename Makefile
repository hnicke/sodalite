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


root =
prefix = /usr
docs = ${root}${prefix}/share/doc/sodalite
share = ${root}${prefix}/share/sodalite
man1 = ${root}${prefix}/share/man/man1
install-misc:
	install -Dm755 scripts/sodalite-open "${root}${prefix}/bin/sodalite-open"
	install -Dm644 sodalite.desktop "${root}${prefix}/share/applications/sodalite.desktop"
	install -Dm644 docs/sodalite.1 "${man1}/sodalite.1"
	install -Dm644 docs/sodalite-open.1 "${man1}/sodalite-open.1"
	install -Dm644 README.md "${docs}/README"
	install -Dm644 copyright "${docs}/copyright"
	install -Dm644 CHANGELOG.md "${docs}/changelog"
	install -Dm644 scripts/shell-integration.sh "${share}/shell-integration.sh"
	install -Dm644 scripts/shell-integration.fish "${share}/shell-integration.fish"
	install -Dm644 sodalite/core/sodalite.conf "${share}/sodalite.conf"

