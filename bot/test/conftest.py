import pytest
import discord
from discord import Message, Member, Guild
from utils.constants import pytest_id
from unittest.mock import MagicMock
from core import Core


@pytest.fixture
def mock_guild():
    return build_mock_guild()


def build_mock_guild():
    guild = MagicMock(spec=Guild)
    guild.id = 123456789
    guild.name = "Test Server"
    return guild


@pytest.fixture
def mock_member():
    return build_mock_member()


def build_mock_member():
    member = MagicMock(spec=Member)
    member.guild = build_mock_guild()
    member.bot = False
    member.roles = []
    member.id = pytest_id
    return member


@pytest.fixture
def mock_message():
    return build_mock_message()


def build_mock_message(content: str = "", id: int = 123456789):
    message = MagicMock(spec=Message)
    message.author = build_mock_member()
    message.guild = build_mock_guild()
    message.content = content
    message.id = id
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
