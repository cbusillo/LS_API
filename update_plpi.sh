#!/bin/bash
python -m build . --wheel
python -m twine upload --skip-existing dist/*


