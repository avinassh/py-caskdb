FILES_TO_LINT=tests/ *.py

run:
	python3 example.py

test:
	python -m unittest discover -vvv ./tests -p '*.py' -b

lint:
	black --check --diff $(FILES_TO_LINT)
	flake8 $(FILES_TO_LINT)
	mypy --strict $(FILES_TO_LINT)
	pytype $(FILES_TO_LINT)

coverage:
	coverage run -m unittest discover -vvv ./tests -p '*.py' -b
	coverage report -m

html: coverage
	coverage html
	open htmlcov/index.html

clean:
	python setup.py clean
	rm -rf build dist cdbpie.egg-info

build: clean
	python setup.py sdist bdist_wheel
