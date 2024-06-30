from apps import BoinkApp, DefApp, TrackerApp
from factory import AppFactory
from mocks import MockMember, MockMessage

MESSAGE_1 = MockMessage(content="!boink keyword some text here")
MESSAGE_2 = MockMessage(content="!tracker keyword some text here")
MESSAGE_3 = MockMessage(content="!def keyword some text here")
MESSAGE_4 = MockMessage(content="boink keyword some text here", bot=True)
MESSAGE_5 = MockMessage(content="tracker keyword some text_here")
MESSAGE_6 = MockMessage(content="def keyword some text here")


def test_is_command():
    factory = AppFactory()

    assert factory._is_command(MESSAGE_1)
    assert factory._is_command(MESSAGE_2)
    assert factory._is_command(MESSAGE_3)
    assert not factory._is_command(MESSAGE_4)
    assert not factory._is_command(MESSAGE_5)
    assert not factory._is_command(MESSAGE_6)


def test_is_bot():
    factory = AppFactory()

    assert not factory._is_bot_message(MESSAGE_1)
    assert factory._is_bot_message(MESSAGE_4)


def test_get_application():
    factory = AppFactory()

    assert factory._get_application(MESSAGE_1) == BoinkApp
    assert factory._get_application(MESSAGE_2) == TrackerApp
    assert factory._get_application(MESSAGE_3) == DefApp


def test_get_params():
    factory = AppFactory()

    assert factory._get_params(MESSAGE_1) == ["keyword", "some", "text", "here"]


def test_factory():
    factory = AppFactory()

    m1 = factory.return_app(MESSAGE_1)
    assert isinstance(m1, BoinkApp)
    assert m1.message is not None
    assert m1.keyword == "keyword"
    assert isinstance(m1.message, MockMessage)
    assert isinstance(m1.message.author, MockMember)

    m2 = factory.return_app(MESSAGE_2)
    assert isinstance(m2, TrackerApp)

    m3 = factory.return_app(MESSAGE_3)
    assert isinstance(m3, DefApp)

    m4 = factory.return_app(MESSAGE_4)
    assert m4 is None
