run:
	python3 example.py

test:
	python -m unittest discover ./tests -p '*.py'

coverage:
	coverage run -m unittest discover ./tests -p '*.py'
	coverage report -m

html: coverage
	coverage html
	open htmlcov/index.html