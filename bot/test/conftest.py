import pytest
import discord
from discord import Message, Member, Guild
from unittest.mock import MagicMock
from core import Core


@pytest.fixture
def mock_guild():
    guild = MagicMock(spec=Guild)
    guild.id = 123456789
    guild.name = "Test Server"
    return guild


@pytest.fixture
def mock_member(mock_guild):
    member = MagicMock(spec=Member)
    member.guild = mock_guild
    member.bot = False
    member.roles = []
    return member


@pytest.fixture
def mock_message(mock_member, mock_guild):
    message = MagicMock(spec=Message)
    message.author = mock_member
    message.guild = mock_guild
    message.content = ""
    return message


@pytest.fixture
def mock_discord_client():
    discord_mock = MagicMock(spec=discord.Client)
    return discord_mock


@pytest.fixture
def mock_core(mock_discord_client):
    intents = discord.Intents.all()
    intents.message_content = True
    core = Core(intents=intents)
    core.client = mock_discord_client
    return core
