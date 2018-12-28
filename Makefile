.PHONY : html lint test serve

html :
	make -C docs html

lint :
	mypy picard tests examples/hello/make.py
	pylint picard tests

serve :
	sphinx-autobuild docs docs/_build/html --host 0.0.0.0 --watch .

test :
	pytest --cov=picard --doctest-modules --ignore=docs
	$(MAKE) -C examples/hello test
