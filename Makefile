run:
	python3 example.py

test:
	python -m unittest discover -vvv ./tests -p '*.py'

lint:
	black --check --diff .
	flake8 .
	mypy --strict .

coverage:
	coverage run -m unittest discover -vvv ./tests -p '*.py' -b
	coverage report -m

html: coverage
	coverage html
	open htmlcov/index.html