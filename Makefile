.PHONY : lint test

lint :
	mypy .
	pylint picard tests

test :
	pytest --cov=picard --doctest-modules
	@rm -f hello*
	python tests/hello.py --help
	python tests/hello.py
	@# A second time just to make sure it does minimal work.
	python tests/hello.py
	./hello
	@rm -f hello*
