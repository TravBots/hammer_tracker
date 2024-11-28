import factory
from handlers.boink_app import BoinkApp
from handlers.def_app import DefApp
from handlers.tracker_app import TrackerApp

from mocks import *


MESSAGE_1 = MockMessage(content="!boink keyword some text here")
MESSAGE_2 = MockMessage(content="!tracker keyword some text here")
MESSAGE_3 = MockMessage(content="!def keyword some text here")
MESSAGE_4 = MockMessage(content="boink keyword some text here", bot=True)
MESSAGE_5 = MockMessage(content="tracker keyword some text_here")
MESSAGE_6 = MockMessage(content="def keyword some text here")


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
