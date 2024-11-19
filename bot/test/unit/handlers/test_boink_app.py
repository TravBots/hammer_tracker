import pytest
from core import Core
from unittest.mock import AsyncMock
from utils.constants import Colors, pytest_id


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
        mock_core.config[str(mock_message.guild.id)]["game_server"] = "test_server"

        # Act
        await mock_core.on_message(mock_message)

        # Assert
        mock_message.channel.send.assert_called_once()
        sent_embed = mock_message.channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.SUCCESS

    # @pytest.mark.asyncio
    # async def test_set_command_admin_role(self, mock_message, mock_core):
    #     # Arrange
    #     mock_message.content = "!boink set admin_role Admin"
    #     app = BoinkApp(mock_message, ["set", "admin_role", "Admin"], mock_core)

    #     # Act
    #     await app.run()

    #     # Assert
    #     mock_message.channel.send.assert_called_once()
    #     sent_embed = mock_message.channel.send.call_args[1]["embed"]
    #     assert sent_embed.color == Colors.SUCCESS
    #     assert "admin_role updated" in sent_embed.fields[0].value.lower()

    # @pytest.mark.asyncio
    # async def test_set_command_invalid_key(self, mock_message, mock_core):
    #     # Arrange
    #     mock_message.content = "!boink set invalid_key value"
    #     app = BoinkApp(mock_message, ["set", "invalid_key", "value"], mock_core)

    #     # Act
    #     await app.run()

    #     # Assert
    #     mock_message.channel.send.assert_called_once()
    #     sent_embed = mock_message.channel.send.call_args[1]["embed"]
    #     assert sent_embed.color == Colors.ERROR

    # @pytest.mark.asyncio
    # async def test_search_command(self, mock_message, mock_core):
    #     # Arrange
    #     mock_message.content = "!boink search player_name"
    #     app = BoinkApp(mock_message, ["search", "player_name"], mock_core)

    #     # Mock database connection and cursor
    #     with patch("sqlite3.connect") as mock_connect:
    #         mock_cursor = MagicMock()
    #         mock_connect.return_value.cursor.return_value = mock_cursor
    #         mock_cursor.fetchall.return_value = [
    #             (1, "player_name", 100, "alliance", 50, 50)
    #         ]

    #         # Act
    #         await app.run()

    #         # Assert
    #         mock_message.channel.send.assert_called_once()
    #         sent_embed = mock_message.channel.send.call_args[1]["embed"]
    #         assert sent_embed.color == Colors.SUCCESS

    # @pytest.mark.asyncio
    # async def test_invalid_command(self, mock_message, mock_core):
    #     # Arrange
    #     mock_message.content = "!boink invalid_command"
    #     app = BoinkApp(mock_message, ["invalid_command"], mock_core)

    #     # Act
    #     await app.run()

    #     # Assert
    #     mock_message.channel.send.assert_called_once()
    #     sent_embed = mock_message.channel.send.call_args[1]["embed"]
    #     assert sent_embed.color == Colors.ERROR

    # @pytest.mark.asyncio
    # async def test_permission_error(self, mock_message, mock_core):
    #     # Arrange
    #     mock_message.content = "!boink set admin_role Admin"
    #     mock_core.read_config_str.side_effect = KeyError()
    #     app = BoinkApp(mock_message, ["set", "admin_role", "Admin"], mock_core)

    #     # Act
    #     await app.run()

    #     # Assert
    #     mock_message.channel.send.assert_called_once()
    #     sent_embed = mock_message.channel.send.call_args[1]["embed"]
    #     assert sent_embed.color == Colors.ERROR
