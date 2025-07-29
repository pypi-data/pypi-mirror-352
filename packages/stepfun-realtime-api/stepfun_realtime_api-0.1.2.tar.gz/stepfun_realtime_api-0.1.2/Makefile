build:
	uv run python -m build

bump-version:
	uv run bump-my-version bump patch --allow-dirty

publish:
	uv run twine upload dist/*

clean:
	rm -rf build dist *.egg-info

.PHONY: build publish bump-version clean
