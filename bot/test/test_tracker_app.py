import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from utils.constants import Colors, pytest_id
from utils.config_manager import update_config

MOCK_GAME_SERVER = "https://ts2.x1.america.travian.com"
MOCK_DB = "test_db.db"


class TestTrackerApp:
    @pytest.mark.asyncio
    async def test_add_command_valid(self, mock_message, mock_core):
        # Arrange
        mock_message.content = (
            "!tracker add PlayerName https://example.com/report 50|50 Test notes"
        )
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id
        mock_message.guild.id = 1234

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_add_command_invalid_coords(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker add PlayerName https://example.com/report invalid|coords Test notes"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id
        mock_message.guild.id = 1234

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_connect.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.ERROR

    @pytest.mark.asyncio
    async def test_get_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker get PlayerName"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)
        update_config(str(mock_message.guild.id), "game_server", MOCK_GAME_SERVER)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()
            mock_connect.return_value.execute.return_value = [
                (
                    1,  # ID
                    "PlayerName",  # IGN
                    "https://example.com",  # LINK
                    "50|50",  # COORDINATES
                    "2024-01-01 12:00:00",  # datetime(TIMESTAMP)
                    "Test notes",  # NOTES
                )
            ]

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_get_command_no_notes(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker get PlayerName"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)
        update_config(str(mock_message.guild.id), "game_server", MOCK_GAME_SERVER)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()
            mock_connect.return_value.execute.return_value = [
                (
                    1,  # ID
                    "PlayerName",  # IGN
                    "https://example.com",  # LINK
                    "50|50",  # COORDINATES
                    "2024-01-01 12:00:00",  # datetime(TIMESTAMP)
                )
            ]

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_get_command_forward_slash(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker get PlayerName"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)
        update_config(str(mock_message.guild.id), "game_server", MOCK_GAME_SERVER)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()
            mock_connect.return_value.execute.return_value = [
                (
                    1,  # ID
                    "PlayerName",  # IGN
                    "https://example.com",  # LINK
                    "50/50",  # COORDINATES
                    "2024-01-01 12:00:00",  # datetime(TIMESTAMP)
                )
            ]

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_delete_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker delete PlayerName 1"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id
        mock_message.author.guild_permissions.administrator = True

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()
            # Mock the returning clause from delete query
            mock_connect.return_value.execute.return_value = [
                (
                    1,  # ID
                    "PlayerName",  # IGN
                    "https://example.com",  # LINK
                    "50|50",  # COORDINATES
                    "2024-01-01 12:00:00",  # TIMESTAMP
                    "Test notes",  # NOTES
                )
            ]

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.WARNING

    @pytest.mark.asyncio
    async def test_list_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker list"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add required config values
        update_config(str(mock_message.guild.id), "database", MOCK_DB)

        # Mock database connection
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.return_value.execute = MagicMock()
            # Mock response for list query which returns IGN, COORDINATES, and timestamp
            mock_connect.return_value.execute.return_value = [
                (
                    "PlayerName1",  # IGN
                    "50|50",  # COORDINATES
                    "2024-01-01 12:00:00",  # datetime(max(timestamp), '-4 hours')
                ),
                (
                    "PlayerName2",  # IGN
                    "100|100",  # COORDINATES
                    "2024-01-01 13:00:00",  # datetime(max(timestamp), '-4 hours')
                ),
            ]

            # Act
            await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_invalid_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker invalid_command"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.ERROR

    @pytest.mark.asyncio
    async def test_permission_error(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!tracker delete PlayerName 1"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = str(pytest_id) + "z"
        mock_message.author.guild_permissions.administrator = False

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.ERROR
