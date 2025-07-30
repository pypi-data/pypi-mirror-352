build:
	python -m build

twine-upload:
	python -m twine upload --repository testpypi dist/* --verbose

remove-dist:
	rm -rf dist orchestration_utils.egg-info
