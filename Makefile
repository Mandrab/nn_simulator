build:
	python -m build

test:
	pytest --cov=nn_simulator test/

install:
	pip install nn_simulator-1.0.0-py3-none-any.whl

venv_on:
	source venv/bin/activate

clear:
	rm -rf build dist .eggs connections.dat datasheet.dat graph.dat wires.dat

.PHONY: build test install venv_on clear
