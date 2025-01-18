source venv/bin/activate
pylint src --check
black src --check
isort src --check
