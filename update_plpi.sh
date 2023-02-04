#!/bin/bash
python -m build . --wheel
python -m twine upload dist/*

