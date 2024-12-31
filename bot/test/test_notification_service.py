import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import datetime
import sqlite3
import discord
from bot.services.notification_service import NotificationService


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

        # Mock channel history to simulate existing delete message
        existing_message = MagicMock(spec=discord.Message)
        existing_message.content = "Player Test Player has deleted their account."
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
