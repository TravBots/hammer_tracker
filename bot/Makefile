VENV = env
BIN=$(VENV)/bin

$(VENV):
	@if [ ! -d env/ ]; then \
		echo "Creating a virtual environment and installing dependencies..."; \
	fi;
	@python3 -m venv $(VENV)
	@$(BIN)/pip install --upgrade -q pip
	@$(BIN)/pip install -q -r requirements.txt

dev: $(VENV)
	@$(BIN)/python core.py

lint: $(VENV)
	@$(BIN)/python -m ruff check

format: $(VENV)
	@$(BIN)/python -m ruff format

test: $(VENV)
	@$(BIN)/python -m pytest test/

clean:
	@rm -rf env/ .ruff_cache/ \
	src/bot/__pycache__ \
	tests/__pycache__ .pytest_cache/

reset: clean $(VENV)

todo:
	@grep -inr "todo" commands/ handlers/ interactions/ utils/ databases/
