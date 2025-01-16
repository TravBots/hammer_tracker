import datetime
import discord
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sqlite3
from services.notification_service import NotificationService
from utils.constants import Colors, NotificationFlags


@pytest.fixture
async def notification_service():
    service = NotificationService()

    # Mock guild and channel
    guild = MagicMock(spec=discord.Guild)
    channel = AsyncMock(spec=discord.TextChannel)
    guild.text_channels = [channel]

    # Set up basic channel configuration
    channel.name = "testplayer"
    channel.send = AsyncMock()

    # Properly mock history for async iteration
    mock_history = AsyncMock()
    mock_history.return_value.__aiter__.return_value = []
    channel.history = mock_history

    return service, guild, channel


@pytest.mark.asyncio
class TestNotificationService:
    async def test_alliance_change_messages(self, notification_service):
        service, guild, channel = notification_service

        # Setup mocks
        mock_conn = MagicMock(spec=sqlite3.Connection)
        with patch(
            "services.notification_service.get_alliance_tag_from_id"
        ) as mock_get_alliance:
            mock_get_alliance.side_effect = ["OLD", "NEW"]

            # Create test data - valid timestamp (today)
            today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            test_data = [
                (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
            ]
            mock_conn.execute.return_value = test_data

            # Execute test
            await service._send_alliance_change_alert(mock_conn, guild)

            # Verify alert was sent with correct message
            channel.send.assert_called_once_with(
                "Player Test Player has changed alliances from **NEW** to **OLD**"
            )

    async def test_channel_not_found(self, notification_service):
        service, guild, channel = notification_service
        # Setup mocks
        mock_conn = MagicMock(spec=sqlite3.Connection)
        guild.text_channels = []  # No channels available

        # Create test data
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Different Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await service._send_alliance_change_alert(mock_conn, guild)

        # Verify no alerts were sent
        assert not channel.send.called

    async def test_send_alerts_old_data(self, notification_service):
        service, guild, channel = notification_service
        # Setup mocks
        mock_conn = MagicMock(spec=sqlite3.Connection)

        # Create test data - old timestamp
        old_date = (datetime.datetime.utcnow() - datetime.timedelta(days=2)).strftime(
            "%Y-%m-%d"
        )
        test_data = [
            (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, old_date)
        ]
        mock_conn.execute.return_value = test_data

        # Execute test
        await service._send_alliance_change_alert(mock_conn, guild)

        # Verify no alerts were sent
        assert not channel.send.called

    async def test_skip_duplicate_alliance_alert(self, notification_service):
        service, guild, channel = notification_service
        # Setup mocks
        mock_conn = MagicMock(spec=sqlite3.Connection)

        # Create test data - valid timestamp (today)
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        test_data = [
            (1, "Test Player", "NEW_ID", "OLD_ID", 2, 2, 100, 100, 0, 1, 0, today)
        ]
        mock_conn.execute.return_value = test_data

        # Mock existing message
        existing_message = MagicMock(spec=discord.Message)
        existing_message.content = (
            "Player Test Player has changed alliances from **OLD** to **NEW**"
        )
        channel.history.return_value.flatten.return_value = [existing_message]

        # Execute test
        await service._send_alliance_change_alert(mock_conn, guild)

        # Verify no new alert was sent
        assert not channel.send.called

    async def test_send_new_village_alert(self, notification_service):
        service, guild, channel = notification_service

        # Setup mocks
        mock_conn = MagicMock(spec=sqlite3.Connection)

        # Create notification channel
        notif_channel = AsyncMock(spec=discord.TextChannel)
        notif_channel.name = "new-villages"
        notif_channel.send = AsyncMock()
        guild.text_channels = [notif_channel]

        # Mock history for duplicate check
        mock_history = AsyncMock()
        mock_history.return_value.__aiter__.return_value = []
        notif_channel.history = mock_history

        # Create test data
        test_data = [
            ("Test Player", -100, 100, 200, "ALLIANCE1"),
            ("Test Player 2", -50, 150, 300, "ALLIANCE1"),
        ]
        mock_conn.execute.return_value = test_data

        # Mock config reads
        with patch("services.notification_service.read_config_str") as mock_config:
            mock_config.side_effect = [
                "ALLIANCE1",  # enemy_alliances
                "NW",  # home_quad
                "new-villages",  # notif_channel
            ]

            # Execute test
            await service._send_new_village_alert(mock_conn, guild)

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
