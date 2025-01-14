import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import datetime
import sqlite3
import discord
from bot.services.notification_service import NotificationService
from bot.utils.constants import Colors, NotificationFlags


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.service = NotificationService()

        # Mock guild
        self.guild = MagicMock(spec=discord.Guild)
        self.guild.id = 123456

        # Mock channel
        self.channel = AsyncMock(spec=discord.TextChannel)
        self.channel.name = "test-player"
        self.channel.send = AsyncMock()

        # Mock guild.text_channels for discord.utils.get
        self.guild.text_channels = [self.channel]

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    @patch("bot.services.notification_service.get_alliance_tag_from_id")
    async def test_send_alerts_valid_data(
        self, mock_get_alliance, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection and cursor
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Mock alliance tags
        mock_get_alliance.side_effect = ["OLD", "NEW"]

        # Create test data - valid timestamp (today)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            # player_id, name, current_alliance, prev_alliance, curr_villages, prev_villages,
            # curr_pop, prev_pop, villages_changed, alliance_changed, pop_change, timestamp
            (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify alerts were sent
        self.channel.send.assert_called_once_with(
            "Player Test Player has changed alliances from **OLD** to **NEW**"
        )

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_send_alerts_old_data(self, mock_connect, mock_get_path, mock_config):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data - old timestamp
        old_date = (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime(
            "%Y-%m-%d"
        )
        test_data = [
            (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, old_date)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify no alerts were sent
        self.channel.send.assert_not_called()

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_send_deleted_player_alert(
        self, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data for deleted player (current_population = 0)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Test Player", "ALLIANCE_ID", "OLD_ID", 0, 2, 0, 100, 1, 0, -100, today)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify deletion alert was sent
        self.channel.send.assert_called_once_with(
            "Player Test Player has deleted their account."
        )

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_channel_not_found(self, mock_connect, mock_get_path, mock_config):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Different Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify no alerts were sent (channel not found)
        self.channel.send.assert_not_called()

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    @patch("bot.services.notification_service.get_alliance_tag_from_id")
    async def test_skip_duplicate_alliance_alert(
        self, mock_get_alliance, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection and cursor
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Mock alliance tags
        mock_get_alliance.side_effect = ["OLD", "NEW"]

        # Create test data - valid timestamp (today)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
        ]
        mock_conn.execute.return_value = test_data

        # Mock channel history to simulate existing message
        existing_message = MagicMock(spec=discord.Message)
        existing_message.content = (
            "Player Test Player has changed alliances from **OLD** to **NEW**"
        )
        self.channel.history.return_value.flatten = AsyncMock(
            return_value=[existing_message]
        )

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify no new alert was sent
        self.channel.send.assert_not_called()

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_skip_duplicate_delete_alert(
        self, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data for deleted player (current_population = 0)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Test Player", "ALLIANCE_ID", "OLD_ID", 0, 2, 0, 100, 1, 0, -100, today)
        ]
        mock_conn.execute.return_value = test_data

        # Mock channel history to return an async iterator with the existing message
        existing_message = MagicMock(spec=discord.Message)
        existing_message.content = "Player Test Player has deleted their account."

        async def mock_history(*args, **kwargs):
            yield existing_message

        self.channel.history.return_value = mock_history()

        # Execute test
        await self.service.send_alerts_for_guild(self.guild)

        # Verify no new alert was sent
        self.channel.send.assert_not_called()

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    @patch("bot.services.notification_service.get_alliance_tag_from_id")
    async def test_alliance_change_messages(
        self, mock_get_alliance, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.return_value = "test_server"
        mock_get_path.return_value = "test_path"
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data template - valid timestamp (today)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        base_data = (1, "Test Player", None, None, 2, 2, 100, 100, 0, 1, 0, today)

        test_cases = [
            # (current_alliance, old_alliance, expected_message)
            ("NEW_TAG", None, "Player Test Player joined alliance NEW_TAG."),
            (None, "OLD_TAG", "Player Test Player left alliance OLD_TAG."),
            (
                "NEW_TAG",
                "OLD_TAG",
                "Player Test Player has changed alliances from **OLD_TAG** to **NEW_TAG**",
            ),
        ]

        for current_alliance, old_alliance, expected_message in test_cases:
            # Reset mocks
            self.channel.send.reset_mock()
            self.channel.history.return_value.flatten.return_value = []

            # Update alliance tag mock returns
            mock_get_alliance.side_effect = [current_alliance, old_alliance]

            # Update test data with alliance IDs
            test_data = list(base_data)
            test_data[2] = "NEW_ID" if current_alliance else None
            test_data[3] = "OLD_ID" if old_alliance else None
            mock_conn.execute.return_value = [tuple(test_data)]

            # Execute test
            await self.service.send_alerts_for_guild(self.guild)

            # Verify correct message was sent
            self.channel.send.assert_called_once_with(expected_message)

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_send_new_village_alert(
        self, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.side_effect = [
            "ALLIANCE1,ALLIANCE2",  # enemy_alliances
            "NW",  # home_quad
            "new-villages",  # notif_channel
        ]
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value = mock_conn

        # Create test data for new village
        test_data = [
            # player_name, x, y, population, alliance_tag
            ("Test Player", -100, 100, 200, "ALLIANCE1"),
            ("Test Player 2", -50, 150, 300, "ALLIANCE1"),
        ]
        mock_conn.execute.return_value = test_data

        # Mock notification channel
        notif_channel = AsyncMock(spec=discord.TextChannel)
        notif_channel.name = "new-villages"
        notif_channel.send = AsyncMock()
        self.guild.text_channels = [notif_channel]

        # Execute test
        await self.service._send_new_village_alert(mock_conn, self.guild)

        # Verify alerts were sent
        assert notif_channel.send.call_count == 2

        # Verify first alert content
        first_call_embed = notif_channel.send.call_args_list[0][1]["embed"]
        assert first_call_embed.color.value == Colors.WARNING
        assert first_call_embed.fields[0].name == "New Village Detected!"
        assert "Test Player" in first_call_embed.fields[0].value
        assert "[-100|100]" in first_call_embed.fields[0].value
        assert "200" in first_call_embed.fields[0].value
        assert "ALLIANCE1" in first_call_embed.fields[0].value

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_work_function_new_village_flag(
        self, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.side_effect = [
            "test_server",  # game_server
            "ALLIANCE1,ALLIANCE2",  # enemy_alliances
            "NW",  # home_quad
            "new-villages",  # notif_channel
        ]
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Create test data
        test_data = [("Test Player", -100, 100, 200, "ALLIANCE1")]
        mock_conn.execute.return_value = test_data

        # Mock notification channel
        notif_channel = AsyncMock(spec=discord.TextChannel)
        notif_channel.name = "new-villages"
        notif_channel.send = AsyncMock()
        self.guild.text_channels = [notif_channel]

        # Execute test with NEW_VILLAGE flag
        await self.service.work(self.guild, NotificationFlags.NEW_VILLAGE)

        # Verify alert was sent
        notif_channel.send.assert_called_once()
        sent_embed = notif_channel.send.call_args[1]["embed"]
        assert sent_embed.color.value == Colors.WARNING
        assert sent_embed.fields[0].name == "New Village Detected!"
        assert "Test Player" in sent_embed.fields[0].value
        assert "[-100|100]" in sent_embed.fields[0].value

    @patch("bot.services.notification_service.read_config_str")
    @patch("bot.services.notification_service.get_connection_path")
    @patch("sqlite3.connect")
    async def test_work_function_multiple_flags(
        self, mock_connect, mock_get_path, mock_config
    ):
        # Setup mocks
        mock_config.side_effect = [
            "test_server",  # game_server
            "ALLIANCE1,ALLIANCE2",  # enemy_alliances
            "NW",  # home_quad
            "new-villages",  # notif_channel
        ]
        mock_get_path.return_value = "test_path"

        # Mock database connection
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Create test data for both new village and player deletion
        new_village_data = [("Test Player", -100, 100, 200, "ALLIANCE1")]
        deleted_player_data = [
            (
                1,
                "Test Player",
                "ALLIANCE_ID",
                "OLD_ID",
                0,
                2,
                0,
                100,
                1,
                0,
                -100,
                "2024-03-20",
            )
        ]

        # Setup mock to return different data for different queries
        def mock_execute(query, *args):
            if "v_new_villages" in query:
                return new_village_data
            elif "current_population=0" in query:
                return deleted_player_data
            return []

        mock_conn.execute = MagicMock(side_effect=mock_execute)

        # Mock channels
        notif_channel = AsyncMock(spec=discord.TextChannel)
        notif_channel.name = "new-villages"
        player_channel = AsyncMock(spec=discord.TextChannel)
        player_channel.name = "test-player"
        self.guild.text_channels = [notif_channel, player_channel]

        # Execute test with multiple flags
        await self.service.work(
            self.guild, NotificationFlags.NEW_VILLAGE | NotificationFlags.PLAYER_DELETED
        )

        # Verify both types of alerts were sent
        assert notif_channel.send.call_count == 1  # New village alert
        assert player_channel.send.call_count == 1  # Player deleted alert

        # Verify new village alert content
        new_village_embed = notif_channel.send.call_args[1]["embed"]
        assert new_village_embed.color.value == Colors.WARNING
        assert new_village_embed.fields[0].name == "New Village Detected!"

        # Verify player deleted alert content
        player_deleted_message = player_channel.send.call_args[0][0]
        assert "has deleted their account" in player_deleted_message
