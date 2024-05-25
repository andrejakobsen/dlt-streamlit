lock-deps:
  uv pip compile pyproject.toml -o requirements.txt

install-deps:
  uv pip sync requirements.txt

lock-dev-deps:
  uv pip compile --extra dev pyproject.toml -o dev-requirements.txt

install-dev-deps:
  uv pip sync dev-requirements.txt
