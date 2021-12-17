#!/bin/bash
python -m pip install --upgrade pip
python -m pip install --upgrade build twine
echo
echo "Cleaning up dist directory."
echo
rm -rf dist/*whl
rm -rf dist/*tar.gz
echo
python -m build
python -m twine upload --repository testpypi dist/*
echo
echo "Test install:"
echo "python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps python3-discogs-client"
echo
echo "All good? Upload to real PyPI:"
echo python3 -m twine upload dist/*
echo

