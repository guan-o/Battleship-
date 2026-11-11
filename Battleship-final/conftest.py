"""Make the project root importable for the tests in tests/.

pytest adds this directory to sys.path because conftest.py lives here, so the
tests can simply do ``import combat``.  Nothing else is needed.
"""
