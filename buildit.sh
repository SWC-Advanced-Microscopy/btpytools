# Quick shell script to run common tasks

pytest
python3 -m black ./
python3 setup.py sdist

# then twine upload dist/*
