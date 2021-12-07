dist:
	python setup.py bdist_wheel

test:
	python setup.py pytest

install:
	pip install nanowire_network_simulator-0.1.0-py3-none-any.whl

activate_env:
	source venv/bin/activate

clear:
	rm -rf build dist .eggs

.PHONY: dist test install activate_env clear
