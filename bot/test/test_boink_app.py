import pytest
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch
from utils.constants import Colors, pytest_id

MOCK_GAME_SERVER = "https://ts2.x1.america.travian.com"


class TestBoinkApp:
    @pytest.mark.asyncio
    async def test_init_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!boink init"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id
        mock_message.guild.id = 1234

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS
        assert "Database initialized" in sent_embed.fields[0].value

    @pytest.mark.asyncio
    async def test_info_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!boink info"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add a game_server key to the config
        mock_core.config[str(mock_message.guild.id)]["game_server"] = MOCK_GAME_SERVER

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    @pytest.mark.asyncio
    async def test_set_command_admin_role(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!boink set admin_role Admin"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS
        assert "set admin_role as admin" in sent_embed.fields[0].value.lower()

    @pytest.mark.asyncio
    async def test_search_command(self, mock_message, mock_core):
        # Arrange
        mock_message.content = "!boink search player_name"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = pytest_id

        # Add game_server to config to prevent that error
        mock_core.config[str(mock_message.guild.id)]["game_server"] = MOCK_GAME_SERVER

        # Mock database connection and cursor
        with patch("sqlite3.connect") as mock_connect:
            mock_cursor = MagicMock()
            mock_connect.return_value.cursor.return_value = mock_cursor
            # Update mock data to include column names that match the DataFrame expectations
            mock_cursor.description = [
                ("id", None),
                ("x_coordinate", None),
                ("y_coordinate", None),
                ("tribe_id", None),
                ("village_id", None),
                ("village_name", None),
                ("player_id", None),
                ("player_name", None),
                ("alliance_id", None),
                ("alliance_tag", None),
                ("population", None),
                ("capital", None),
                ("inserted_at", None),
            ]
            mock_cursor.fetchall.return_value = [
                (
                    "50|50@1710936000",  # id (x|y@timestamp format)
                    50,  # x_coordinate
                    50,  # y_coordinate
                    1,  # tribe_id
                    12345,  # village_id
                    "Test Village",  # village_name
                    67890,  # player_id
                    "player_name",  # player_name
                    11111,  # alliance_id
                    "TEST",  # alliance_tag
                    100,  # population
                    False,  # capital
                    1710936000,  # inserted_at (unix timestamp)
                )
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
        mock_message.content = "!boink invalid_command"
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
        mock_message.content = "!boink set admin_role Admin"
        mock_message.channel.send = AsyncMock()
        mock_message.author.id = str(pytest_id) + "z"
        mock_message.author.guild_permissions.administrator = False

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.ERROR
