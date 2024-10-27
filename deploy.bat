pip install build twine
python -m build
twine upload --repository pypi dist/*