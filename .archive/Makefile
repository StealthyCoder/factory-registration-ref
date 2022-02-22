
venv:
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt.pinned

format:
	.venv/bin/black tests/*.py registration_ref/*.py

test:
	.venv/bin/python3 -m unittest discover
