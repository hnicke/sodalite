distDir = dist
pkg = sodalite
mypy = poetry run mypy --config mypy.ini -p ${pkg} -p tests ${shell [ ${color} != 'true' ] && echo '--no-color-output'}
reportDir = ${distDir}/reports



color = true
type-check ${reportDir}/index.txt ${reportDir}/index.html ${reportDir}/linecount.txt: .venv ${pkg} tests
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

.venv: pyproject.toml poetry.lock
	poetry install
	touch .venv

deps: .venv
.PHONY: deps

run: .venv
	poetry run sodalite
.PHONY: run

check: lint type-check test
.PHONY: check

test: .venv
	poetry run pytest tests
.PHONY: test

lint: .venv
	poetry run flake8 ${pkg} tests
.PHONY: lint

prune: clean
	rm -rf .venv
.PHONY: prune

clean:
	rm -rf db.sqlite ${distDir}
.PHONY: clean

release:
	./scripts/release "$${VERSION:?Which version?}"

build: .venv
	poetry build
.PHONY: build

setup-hooks:
	@for file in scripts/hooks/*; do \
		ln -sf ../../$$file .git/hooks/$$(basename $$file); \
		echo Symlinked git hook: $$(basename $$file); \
	done

