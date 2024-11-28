from bot.utils import factory
from handlers.boink_app import BoinkApp
from handlers.def_app import DefApp
from handlers.tracker_app import TrackerApp
from bot.test.conftest import build_mock_message


MESSAGE_1 = build_mock_message(content="!boink keyword some text here")
MESSAGE_2 = build_mock_message(content="!tracker keyword some text here")
MESSAGE_3 = build_mock_message(content="!def keyword some text here")
MESSAGE_4 = build_mock_message(content="boink keyword some text here")
MESSAGE_5 = build_mock_message(content="tracker keyword some text_here")
MESSAGE_6 = build_mock_message(content="def keyword some text here")

MESSAGE_4.author.bot = True


class TestFactory:
    def test_is_command(self):
        assert factory._is_command(MESSAGE_1)
        assert factory._is_command(MESSAGE_2)
        assert factory._is_command(MESSAGE_3)
        assert not factory._is_command(MESSAGE_4)
        assert not factory._is_command(MESSAGE_5)
        assert not factory._is_command(MESSAGE_6)

    def test_is_bot(self):
        assert not factory._is_bot_message(MESSAGE_1)
        assert factory._is_bot_message(MESSAGE_4)

    def test_get_application(self):
        assert isinstance(factory.get_app(MESSAGE_1), BoinkApp)
        assert isinstance(factory.get_app(MESSAGE_2), TrackerApp)
        assert isinstance(factory.get_app(MESSAGE_3), DefApp)
