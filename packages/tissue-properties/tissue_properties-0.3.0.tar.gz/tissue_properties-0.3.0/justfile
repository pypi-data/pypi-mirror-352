set positional-arguments

default:
  just --list


pytest *args:
  cd {{ justfile_directory()/"tests" }} && uv run pytest -s "$@"

publish:
  rm dist -rf
  uv build
  uv publish
