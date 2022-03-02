# Quick shell script to run common tasks

pytest-3 tests/tests/basic.py
python3 -m black ./
python3 setup.py sdist

# then twine upload dist/*
