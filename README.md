# Travstat Bot & Dashboard

A Discord bot and web dashboard for tracking and analyzing Travian game data. The project consists of two main components:

- A Discord bot for managing defense coordination and player tracking
- A web dashboard for visualizing game data and statistics

## Features

### Discord Bot

- **Defense Coordination**

  - Create and manage defense calls (CFDs)
  - Track defense contributions
  - View defense leaderboards
  - Organize defense through threaded discussions

- **Player Tracking**

  - Record and retrieve player reports
  - Search player rankings and statistics
  - Monitor player village changes

- **Server Management**
  - Server-specific configurations
  - Role-based access control
  - Automated alerts for alliance changes

### Web Dashboard

- **Interactive World Map**

  - Filter alliances
  - View player villages and populations
  - Track territory control

- **Analytics**
  - Alliance population trends
  - Player growth statistics
  - Village distribution analysis

## Installation

### Prerequisites

- Python 3.8+
- SQLite3
- Discord Bot Token

### Bot Setup

1. Clone the repository
2. Create a virtual environment:

```python
python -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `config.ini` in the bot directory:

```ini
[default]
token = YOUR_DISCORD_BOT_TOKEN
database = databases/default.db

[meta]
database = databases/meta.db
```

5. Initialize the database structure:

```bash
python databases/manage.py --refresh-views
```

### Dashboard Setup

1. Navigate to the site directory
2. Install dashboard dependencies:

```bash
pip install -r site/requirements.txt
```

3. Start the dashboard:

```bash
python site/app.py
```

## Bot Commands

### Defense Commands

- `!def list` - List open defense calls
- `!def send <cfd_id> <amount>` - Submit defense to a CFD
- `!def leaderboard` - View defense contribution rankings
- `!def log` - View defense submission history

### Tracker Commands

- `!tracker add <ign> <link> <coordinates>` - Add a player report
- `!tracker get <ign> [count]` - Get player reports
- `!tracker list` - List all tracked players
- `!tracker delete <ign> <report_id>` - Delete a report

### Admin Commands

- `!boink init` - Initialize server configuration
- `!boink info` - View server settings
- `!boink set <setting> <value>` - Update server settings

## Permissions

The bot uses a role-based permission system:

- **Admin Role**: Full access to all commands
- **User Role**: Access to basic tracking and viewing commands
- **Anvil Role**: Special access to defense coordination

## Database Structure

The project uses two types of databases:

- **Bot Servers**: Individual databases for each Discord server
- **Game Servers**: Databases containing Travian game data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Discord.py for the bot framework
- Dash for the web dashboard
- Plotly for data visualization

### Available Commands

All commands must be run from the `bot` directory.

#### Run Tests

```bash
./commands.sh test [test_file]
```

Runs pytest for all tests or a specific test file.

- Without argument: Runs all tests in `test/` directory
- With argument: Runs specific test file (omit .py extension)  
  Example: `./commands.sh test test_boink_app`

#### Run Development Mode

```bash
./commands.sh dev
```

Runs the bot in development mode.
