build:
	python -m build

test:
	pytest

install:
	pip install nanowire_network_simulator-1.0.0-py3-none-any.whl

activate_env:
	source venv/bin/activate

clear:
	rm -rf build dist .eggs connections.dat datasheet.dat graph.dat wires.dat

.PHONY: build test install activate_env clear
