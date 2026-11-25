.PHONY: run test clean install

install:
	pip install -r requirements.txt

run:
	python -m src.cli -f examples/db_config.cfg

test:
	python -m unittest discover tests

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
