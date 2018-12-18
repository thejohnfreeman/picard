.PHONY : lint test

lint :
	mypy .
	pylint picard tests

test :
	pytest
	@rm -f hello*
	python tests/hello.py --help
	python tests/hello.py
	./hello
	@rm -f hello*
