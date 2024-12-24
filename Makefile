VENV = env
BIN=$(VENV)/bin
CONFIG = bot/config.ini

$(VENV):
	@if [ ! -d env/ ]; then \
		echo "Creating a virtual environment and installing dependencies..."; \
	fi;
	@python -m venv $(VENV)
	@$(BIN)/pip install --upgrade -q pip
	@$(BIN)/pip install -q -r bot/requirements.txt
	@$(BIN)/pip install -q -r databases/requirements.txt
	@$(BIN)/pip install -q -r site/requirements.txt

setup:
	@if [ ! -d databases/bot_servers ]; then \
		mkdir -p databases/bot_servers; \
	fi
	@if [ ! -d databases/game_servers ]; then \
		mkdir -p databases/game_servers; \
	fi
	@if [ ! -d databases/analytics ]; then \
		mkdir -p databases/analytics; \
	fi
	@if [ ! -f $(CONFIG) ]; then \
		echo "[default]" > $(CONFIG); \
		echo "token = $${DISCORD_BOT_TOKEN}" >> $(CONFIG); \
		echo "database = databases/default.db" >> $(CONFIG); \
		echo "" >> $(CONFIG); \
		echo "[meta]" >> $(CONFIG); \
		echo "database = databases/meta.db" >> $(CONFIG); \
	fi

bot-run: $(VENV)
	@cd bot && $(BIN)/python core.py

bot-lint: $(VENV)
	@cd bot && $(BIN)/python -m ruff check

bot-format: $(VENV)
	@cd bot && $(BIN)/python -m ruff format

bot-test: $(VENV)
	@cd bot && $(BIN)/python -m pytest test/ -v -s --log-cli-level=DEBUG

site-run: $(VENV)
	@cd site && $(BIN)/python app.py

clean:
	@rm -rf env/ .ruff_cache/ \
	bot/__pycache__ \
	bot/test/__pycache__ \
	bot/.pytest_cache/ \
	site/__pycache__ \
	databases/__pycache__

reset: clean $(VENV)

todo:
	@grep -inr "todo" bot/commands/ bot/handlers/ bot/interactions/ bot/utils/ databases/

.PHONY: setup bot-run bot-test bot-lint bot-format dev-site clean reset todo 