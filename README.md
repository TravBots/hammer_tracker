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
2. Run the setup script with your Discord bot token:

```bash
# This will:
# -- Create necessary database directories
# -- Create config.ini with your bot token
# -- Set up the database structure

./setup.sh YOUR_DISCORD_BOT_TOKEN
```

3. Create virtual environment and install dependencies:

```bash
# This will:
# -- Create a new virtual environment
# -- Install all required dependencies
# -- Clean any existing caches/temporary files

cd bot
make reset
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

### Development Commands

All commands must be run from the `bot` directory.

#### Run Tests

```bash
make test
```

Runs pytest for all tests in the `test/` directory.

#### Run Development Mode

```bash
make dev
```

Runs the bot in development mode.

#### Code Formatting and Linting

```bash
make format  # Format code using ruff
make lint    # Run linting checks
```

#### Clean Environment

```bash
make reset   # Clean and recreate virtual environment
```
