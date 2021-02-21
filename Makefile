.PHONY: test clean

default: test

help:
	@echo 'Management commands:'
	@echo
	@echo 'Usage:'
	@echo '    make build           Compile the project.'
	@echo '    make test            Run tests on a compiled project.'
	@echo

build:
	docker-compose build

up:
	docker-compose up

test:
	docker-compose -f docker-compose.test.yml run --rm test pytest $(file)

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +