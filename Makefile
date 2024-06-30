VENV = env
BIN=$(VENV)/bin

$(VENV):
	@if [ ! -d env/ ]; then \
		echo "Creating a virtual environment and installing dependencies..."; \
	fi;
	@python3 -m venv $(VENV)
	@$(BIN)/pip install --upgrade -q pip
	@$(BIN)/pip install -r requirements.txt

lint: $(VENV)
	@$(BIN)/python -m ruff check

format: $(VENV)
	@$(BIN)/python -m ruff format

test: $(VENV)
	@$(BIN)/python -m pytest

pull-prod-dbs: $(VENV)
	@cd databases && ../$(BIN)/python manage.py copy-prod-db $(username)

setup-game-dbs: $(VENV)
	@cd databases && ../$(BIN)/python load.py && ../$(BIN)/python manage.py refresh-views

run-site: $(VENV)
	@cd site && ../$(BIN)/python app.py

run-bot: $(VENV)
	@cd bot && ../$(BIN)/python core.py

# clean:
# 	@rm -rf env/ .ruff_cache/ fable.egg-info/ \
# 	src/fable.egg-info/ src/fable/__pycache__ \
# 	tests/__pycache__ .pytest_cache/ dist/

# reset: clean $(VENV)

todo:
	@grep -inr "todo" bot/ site/
