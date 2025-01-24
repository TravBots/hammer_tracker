VENV = env
BIN=$(VENV)/bin
CONFIG = config.ini

$(VENV):
	@if [ ! -d env/ ]; then \
		echo "Creating a virtual environment and installing dependencies..."; \
	fi;
	@python -m venv $(VENV)
	@$(BIN)/pip install --upgrade -q pip
	@$(BIN)/pip install -q -r requirements.txt

setup:
	@if [ ! -d databases ]; then \
		mkdir databases; \
	fi
	@if [ ! -f $(CONFIG) ]; then \
		echo "[default]" > $(CONFIG); \
		echo "token = $${DISCORD_BOT_TOKEN}" >> $(CONFIG); \
		echo "database = databases/default.db" >> $(CONFIG); \
		echo "" >> $(CONFIG); \
		echo "[meta]" >> $(CONFIG); \
		echo "database = databases/meta.db" >> $(CONFIG); \
	fi

dev: $(VENV)
	@$(BIN)/python core.py

dev-debug: $(VENV)
	@$(BIN)/python core.py --log-level=DEBUG

lint: $(VENV)
	@$(BIN)/python -m ruff check

format: $(VENV)
	@$(BIN)/python -m ruff format

test: $(VENV)
	@$(BIN)/python -m pytest test/ -v -s --log-cli-level=DEBUG

clean:
	@rm -rf env/ .ruff_cache/ \
	src/bot/__pycache__ \
	tests/__pycache__ .pytest_cache/

reset: clean $(VENV)

todo:
	@grep -inr "todo" commands/ handlers/ interactions/ utils/ databases/
