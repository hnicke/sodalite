buildDir = ${CURDIR}/build
sourceDir = ${CURDIR}/source
id = de.hnicke.Sodalite
manifest = ${id}.yml

build: ${buildDir}
.PHONY: build

${buildDir}: ${manifest}
	rm -rf ${sourceDir}
	mkdir ${sourceDir}
	( cd ../../ && cp -r $$(ls -1 | grep -v packaging) ${sourceDir}/ )
	make -C ${sourceDir} prune
	## TODO GPG signing
	flatpak-builder --force-clean --user --install ${buildDir} ${manifest}
	rm -rf ${sourceDir}
.PHONY: ${buildDir}

run:
	flatpak run ${id}
.PHONY: run

clean:
	${buildDir} ${sourceDir}
.PHONY: clean
