@echo off
REM Upgrade pip, build, and twine
py -m pip install --upgrade pip build twine

REM Build the package (creates dist/*.whl and dist/*.tar.gz)
py -m build

REM Upload to PyPI (production)
py -m twine upload dist/* 