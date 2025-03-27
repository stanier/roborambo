#!/usr/bin/env make

ignore_errors = > /dev/null 2>&1 || true
python_version = python3.11
cosmo_url = https://cosmo.zip/pub/cosmocc/cosmocc.zip

all: clean dependencies pyinstall test

clean_vendor:
	@rm -r ${PWD}/vendor $(ignore_errors)

clean:
	@rm -r ${PWD}/build $(ignore_errors)
	@rm -r ${PWD}/roborambo.egg-info $(ignore_errors)
	@rm -r ${PWD}/*/roborambo.egg-info $(ignore_errors)
	@rm -r ${PWD}/nothingburger.egg-info $(ignore_errors)
	@rm -r ${PWD}/*/nothingburger.egg-info $(ignore_errors)

clean_venv:
	@echo "Just dropping your venv, don't panic"
	rm -rf ${PWD}/venv
	rm -rf ${PWD}/*/venv

pyinstall: dependencies
	if [ ! -d "${PWD}/venv" ]; then \
		${python_version} -m venv venv; \
	fi

	. ${PWD}/venv/bin/activate; \
	${PWD}/venv/bin/${python_version} -m pip install --no-deps ${PWD}/vendor/nothingburger/ ${PWD}

compile: build
	. ${PWD}/venv/bin/activate; ${PWD}/venv/bin/${python_version} setup.py build_ext --inplace

polish:
	mkdir -p dist/roborambo
	bash -c "vendor/cosmocc/bin/cosmocc -o dist/roborambo/roborambo examples/roborambo.c"

test:

dependencies: #get_cosmo
	. ${PWD}/venv/bin/activate; \
	${PWD}/venv/bin/${python_version} -m pip install --no-deps -U ${PWD}/vendor/nothingburger/ ${PWD}

	if [ ! -d "${PWD}/venv" ]; then \
		${python_version} -m venv venv; \
	fi

	. ${PWD}/venv/bin/activate; \
	${PWD}/venv/bin/${python_version} -m pip install -U ${PWD}/vendor/nothingburger/ ${PWD}

get_cosmo:
	mkdir -p vendor/cosmocc
	cd vendor/cosmocc && wget ${cosmo_url} && unzip cosmocc.zip

